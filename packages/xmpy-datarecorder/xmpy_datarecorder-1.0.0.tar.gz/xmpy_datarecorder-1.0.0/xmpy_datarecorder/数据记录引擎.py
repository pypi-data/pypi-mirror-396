import traceback
from threading import Thread
from queue import Queue, Empty
from copy import copy
from collections import defaultdict
from typing import Optional
from datetime import datetime, timedelta

from xmpy.包_事件引擎 import 类_事件,类_事件引擎
from xmpy.包_交易核心 import 模块_对象
from xmpy.包_交易核心.模块_主引擎 import 基础引擎, 类_主引擎, 日志引擎
from xmpy.包_交易核心.模块_常数 import 类_交易所
from xmpy.包_交易核心.模块_对象 import (
    类_订阅请求,
    类_行情数据,
    类_K线数据,
    类_合约数据,
    类_日志数据,
    类_价差项
)
from xmpy.包_交易核心.模块_事件类型 import 事件类型_行情,事件类型_合约,事件类型_定时
from xmpy.包_交易核心.模块_工具 import 加载json文件,保存json文件,类_K线生成器,爬取主力合约表格,处理合约信息
from xmpy.包_交易核心.模块_基础数据库 import 获取数据库,数据库时区


应用名称 = "数据记录器"

事件类型_记录日志 = "记录日志"
事件类型_记录更新 = "记录更新"
事件类型_记录异常 = "记录异常"
事件类型_价差数据 = "价差数据更新"


class 类_记录引擎(基础引擎):
    """数据记录引擎，用于运行数据记录功能"""

    配置文件名 = "自选合约配置.json"

    def __init__(self, 主引擎: 类_主引擎, 事件引擎: 类_事件引擎) -> None:
        """构造函数"""
        super().__init__(主引擎, 事件引擎, 应用名称)

        self.所有策略: dict = {}  # 策略名称: 策略实例
        self.策略配置: dict = {}  # 策略名称: 配置字典

        self.任务队列: Queue = Queue()
        self.工作线程 = Thread(target=self.运行)
        self.运行状态 = False

        self.tick记录字典 = {}
        self.k线记录字典 = {}
        self.k线生成器字典 = {}

        self.定时计数 = 0
        self.定时间隔 = 10

        self.tick缓存: dict[str, list[类_行情数据]] = defaultdict(list)
        self.k线缓存: dict[str, list[类_K线数据]] = defaultdict(list)

        self.过滤时间 = datetime.now(数据库时区)
        self.过滤窗口 = 60
        self.时间差 = None

        self.数据库 = 获取数据库()

        self.加载配置()
        self.注册事件()
        self.启动()
        爬取主力合约表格()

        self.发送更新事件()

    def 加载配置(self) -> None:
        """加载配置文件"""
        配置 = 加载json文件(self.配置文件名)
        self.tick记录字典 = 配置.get("tick", {})
        self.k线记录字典 = 配置.get("K线", {})

        self.过滤窗口 = 配置.get("过滤窗口", 60)
        self.时间差 = timedelta(seconds=self.过滤窗口)

    def 保存配置(self) -> None:
        """保存配置文件"""
        配置 = {
            "tick": self.tick记录字典,
            "K线": self.k线记录字典,
        }
        保存json文件(self.配置文件名, 配置)

    def 更新配置(self, 策略名称: str, 配置字典: dict) -> None:
        """更新策略配置到文件"""
        策略实例 = self.所有策略[策略名称]
        self.策略配置[策略名称] = {
            "class_name": 策略实例.__class__.__name__,
            "vt_symbol": 策略实例.合约标识,
            "setting": 配置字典,
        }
        保存json文件(self.配置文件名, self.策略配置)

    def 运行(self) -> None:
        """工作线程主循环"""
        while self.运行状态:
            try:
                任务: 模块_对象 = self.任务队列.get(timeout=1)
                任务类型, 数据 = 任务

                if 任务类型 == "tick":
                    self.数据库.保存Tick数据(数据, 流式存储 = True)
                elif 任务类型 == "k线":
                    self.数据库.保存K线数据(数据, 流式存储 = True)

            except Empty:
                continue

            except Exception:
                self.运行状态 = False
                异常信息 = traceback.format_exc()
                事件 = 类_事件(事件类型_记录异常, 异常信息)
                self.事件引擎.放入事件(事件)

    def 关闭(self) -> None:
        """关闭引擎"""
        self.运行状态 = False
        if self.工作线程.is_alive():
            self.工作线程.join()

    def 启动(self) -> None:
        """启动引擎"""
        self.运行状态 = True
        self.工作线程.start()

    def 启动自选合约采集(self) -> None:
        # 合并两个字典的键，避免重复处理
        所有合约键 = set(self.k线记录字典.keys()) | set(self.tick记录字典.keys())

        for 代码_交易所 in 所有合约键:
            # 检查是否为本地数据
            if 类_交易所.本地数据.value not in 代码_交易所:
                # 非本地数据合约需要订阅
                合约: Optional[类_合约数据] = self.主引擎.获取合约详情(代码_交易所)
                if not 合约:
                    self.记录日志(f"找不到合约：{代码_交易所}")
                    continue  # 继续处理其他合约，而不是直接返回

                self.订阅合约(合约)
            else:
                # 本地数据合约初始化字典
                self.k线记录字典[代码_交易所] = {}
                self.tick记录字典[代码_交易所] = {}

    def 启动主力合约采集(self, tick记录 = True, K线记录 = True, 交易所名称: str = "全部"):
        主力合约列表 = 处理合约信息(交易所名称)

        for 代码_交易所 in 主力合约列表:
            if 类_交易所.本地数据.value not in 代码_交易所:
                # 非本地数据合约需要订阅
                合约: Optional[类_合约数据] = self.主引擎.获取合约详情(代码_交易所)
                if not 合约:
                    self.记录日志(f"找不到合约：{代码_交易所}")
                    continue  # 继续处理其他合约，而不是直接返回

                if tick记录:
                    self.tick记录字典[代码_交易所] = {
                        "合约代码": 合约.代码,
                        "交易所": 合约.交易所.value,
                        "网关名称": 合约.网关名称
                    }
                if K线记录:
                    self.k线记录字典[代码_交易所] = {
                        "合约代码": 合约.代码,
                        "交易所": 合约.交易所.value,
                        "网关名称": 合约.网关名称
                    }

                self.订阅合约(合约)

            else:
                # 本地数据合约初始化字典
                self.k线记录字典[代码_交易所] = {}
                self.tick记录字典[代码_交易所] = {}

    def 清理过期自选合约(self) -> None:
        # 合并两个字典的键，避免重复处理
        所有合约键 = set(self.k线记录字典.keys()) | set(self.tick记录字典.keys())

        for 代码_交易所 in 所有合约键:
            # 检查是否为本地数据
            if 类_交易所.本地数据.value not in 代码_交易所:
                # 非本地数据合约需要订阅
                合约: Optional[类_合约数据] = self.主引擎.获取合约详情(代码_交易所)
                if not 合约:
                    self.记录日志(f"存在过期合约：{代码_交易所}，开始进行移除")
                    self.移除自选Tick合约(代码_交易所)
                    self.移除自选K线合约(代码_交易所)
                    continue  # 继续处理其他合约，而不是直接返回

    def 添加自选K线合约(self, 代码_交易所: str) -> None:
        """添加K线记录"""
        if 代码_交易所 in self.k线记录字典:
            self.记录日志(f"已在K线记录列表中：{代码_交易所}")

        if 类_交易所.本地数据.value not in 代码_交易所:
            合约: Optional[类_合约数据] = self.主引擎.获取合约详情(代码_交易所)
            if not 合约:
                self.记录日志(f"找不到合约：{代码_交易所}")
                return

            self.k线记录字典[代码_交易所] = {
                "合约代码": 合约.代码,
                "交易所": 合约.交易所.value,
                "网关名称": 合约.网关名称
            }
            self.订阅合约(合约)
        else:
            self.k线记录字典[代码_交易所] = {}

        self.保存配置()
        self.发送更新事件()
        self.记录日志(f"添加K线记录成功：{代码_交易所}")

    def 添加自选Tick合约(self, 代码_交易所: str) -> None:
        """添加Tick记录"""
        if 代码_交易所 in self.tick记录字典:
            self.记录日志(f"已在Tick记录列表中：{代码_交易所}")

        if 类_交易所.本地数据.value not in 代码_交易所:
            合约: Optional[类_合约数据] = self.主引擎.获取合约详情(代码_交易所)
            if not 合约:
                self.记录日志(f"找不到合约：{代码_交易所}")
                return

            self.tick记录字典[代码_交易所] = {
                "合约代码": 合约.代码,
                "交易所": 合约.交易所.value,
                "网关名称": 合约.网关名称
            }
            self.订阅合约(合约)
        else:
            self.tick记录字典[代码_交易所] = {}

        self.保存配置()
        self.发送更新事件()
        self.记录日志(f"添加Tick记录成功：{代码_交易所}")

    def 移除自选K线合约(self, 代码_交易所: str) -> None:
        """移除K线记录"""
        if 代码_交易所 not in self.k线记录字典:
            self.记录日志(f"不在K线记录列表中：{代码_交易所}")
            return

        self.k线记录字典.pop(代码_交易所)
        self.保存配置()
        self.发送更新事件()
        self.记录日志(f"移除K线记录成功：{代码_交易所}")

    def 移除自选Tick合约(self, 代码_交易所: str) -> None:
        """移除Tick记录"""
        if 代码_交易所 not in self.tick记录字典:
            self.记录日志(f"不在Tick记录列表中：{代码_交易所}")
            return

        self.tick记录字典.pop(代码_交易所)
        self.保存配置()
        self.发送更新事件()
        self.记录日志(f"移除Tick记录成功：{代码_交易所}")

    def 注册事件(self) -> None:
        """注册事件监听"""
        self.事件引擎.注册类型处理器(事件类型_定时, self.处理定时事件)
        self.事件引擎.注册类型处理器(事件类型_行情, self.处理tick事件)
        self.事件引擎.注册类型处理器(事件类型_合约, self.处理合约事件)
        self.事件引擎.注册类型处理器(事件类型_价差数据, self.处理价差事件)

        获取日志引擎: 日志引擎 = self.主引擎.获取引擎("日志")
        self.事件引擎.注册类型处理器(事件类型_记录日志, 获取日志引擎.处理日志事件)

    def 更新Tick数据(self, tick: 类_行情数据) -> None:
        """更新Tick数据"""
        tick时间差 = abs(tick.时间戳 - self.过滤时间)

        if abs(tick时间差) >= self.时间差:
            print(f'进入更新Tick数据，空判断，{tick.代码_交易所}')
            return

        if tick.代码_交易所 in self.tick记录字典:
            self.记录Tick(copy(tick))

        if tick.代码_交易所 in self.k线记录字典:
            k线生成器: 类_K线生成器 = self.获取k线生成器(tick.代码_交易所)
            k线生成器.更新Tick(copy(tick))

    def 处理定时事件(self, 事件: 类_事件) -> None:
        """处理定时事件"""
        self.过滤时间 = datetime.now(数据库时区)

        self.定时计数 += 1
        if self.定时计数 < self.定时间隔:
            return
        self.定时计数 = 0

        for k线列表 in self.k线缓存.values():
            self.任务队列.put(("k线", k线列表))
        self.k线缓存.clear()

        for tick列表 in self.tick缓存.values():
            self.任务队列.put(("tick", tick列表))
        self.tick缓存.clear()

    def 处理tick事件(self, 事件: 类_事件) -> None:
        """处理Tick事件"""
        tick: 类_行情数据 = 事件.数据
        self.更新Tick数据(tick)

    def 处理合约事件(self, 事件: 类_事件) -> None:
        """处理合约事件"""
        合约: 类_合约数据 = 事件.数据
        合约代码: str = 合约.代码

        if 合约代码 in self.tick记录字典 or 合约代码 in self.k线记录字典:
            self.订阅合约(合约)

    def 处理价差事件(self, 事件: 类_事件) -> None:
        """处理价差数据事件"""
        价差项: 类_价差项 = 事件.数据
        tick数据: 类_行情数据 = 类_行情数据(
            代码 = 价差项.名称,
            交易所 = 类_交易所.本地数据,
            时间戳 = 价差项.时间,
            名称 = 价差项.名称,
            最新价 = (价差项.买价 + 价差项.卖价) / 2,
            买一价 = 价差项.买价,
            卖一价 = 价差项.卖价,
            买一量 = 价差项.买量,
            卖一量 = 价差项.卖量,
            本地时间 = 价差项.时间,
            网关名称 = "价差"
        )

        if tick数据.时间戳:
            self.更新Tick数据(tick数据)

    def 记录日志(self, 内容: str) -> None:
        """记录引擎日志"""

        日志实例 = 类_日志数据(消息内容=内容, 网关名称=应用名称)
        事件 = 类_事件(类型=事件类型_记录日志, 数据=日志实例)
        self.事件引擎.放入事件(事件)

    def 发送更新事件(self) -> None:
        """推送状态更新事件"""
        tick代码列表 = list(self.tick记录字典.keys())
        tick代码列表.sort()

        k线代码列表 = list(self.k线记录字典.keys())
        k线代码列表.sort()

        数据 = {
            "tick": tick代码列表,
            "k线": k线代码列表
        }

        事件 = 类_事件(事件类型_记录更新, 数据)
        self.事件引擎.放入事件(事件)

    def 记录Tick(self, tick数据: 类_行情数据) -> None:
        """记录Tick数据到缓存"""
        self.tick缓存[tick数据.代码_交易所].append(tick数据)

    def 记录K线(self, k线数据: 类_K线数据) -> None:
        """记录K线数据到缓存"""
        # self.记录日志(f'K线：{k线数据}')
        self.k线缓存[k线数据.代码_交易所].append(k线数据)

    def 获取k线生成器(self, 代码_交易所: str) -> 类_K线生成器:
        """获取K线生成器"""
        生成器: Optional[类_K线生成器] = self.k线生成器字典.get(代码_交易所, None)

        if not 生成器:
            生成器 = 类_K线生成器(self.记录K线)
            self.k线生成器字典[代码_交易所] = 生成器

        return 生成器

    def 订阅合约(self, 合约: 类_合约数据) -> None:
        """订阅合约行情"""
        请求: 类_订阅请求 = 类_订阅请求(
            代码 = 合约.代码,
            交易所 = 合约.交易所
        )
        self.主引擎.订阅行情(请求, 合约.网关名称)