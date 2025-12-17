from abc import ABC
from copy import copy
from typing import Any, Callable

from xmpy.包_交易核心.模块_常数 import 类_周期,类_方向,类_开平
from xmpy.包_交易核心.模块_对象 import 类_K线数据,类_行情数据,类_订单数据,类_成交数据
from xmpy.包_交易核心.模块_工具 import 虚拟方法

from .模块_基础 import 类_停止单, 类_引擎类型


class 类_CTA策略模板(ABC):
    """CTA策略模板基类"""

    作者: str = ""
    参数列表: list = []
    变量列表: list = []

    def __init__(self,CTA引擎: Any,策略名称: str,合约_交易所: str,配置字典: dict,) -> None:
        self.CTA引擎 = CTA引擎
        self.策略名称 = 策略名称
        self.合约_交易所 = 合约_交易所

        # 自动获取所有策略变量名，参数名（包括未在变量列表中声明的，注意：获取到的参数名使用的时候会排除）
        所有策略变量 = self.获取所有策略变量名()

        # 复制所有变量
        self.参数列表 = copy(self.参数列表)  # 实例独立
        self.变量列表 = copy(self.变量列表)  # 实例独立

        self.已初始化: bool = False
        self.运行中: bool = False
        self.多头仓位: int = 0
        self.空头仓位: int = 0

        self.变量列表.insert(0, "已初始化")
        self.变量列表.insert(1, "运行中")
        self.变量列表.insert(2, "多头仓位")
        self.变量列表.insert(3, "空头仓位")

        # 为所有策略变量创建独立副本（排除参数变量）
        for 变量名 in 所有策略变量:
            # 跳过参数列表中的变量
            if 变量名 in self.参数列表:
                continue

            if hasattr(self, 变量名):
                原始值 = getattr(self, 变量名)
                if isinstance(原始值, list):
                    setattr(self, 变量名, copy(原始值))  # 列表浅拷贝
                elif isinstance(原始值, dict):
                    setattr(self, 变量名, 原始值.copy())  # 字典浅拷贝
                elif hasattr(原始值, '__dict__'):  # 处理自定义对象
                    setattr(self, 变量名, copy(原始值))
                else:
                    # 不可变类型直接赋值（后续修改时会创建新对象）
                    setattr(self, 变量名, 原始值)

        self.更新配置(配置字典)

    def 获取所有策略变量名(self) -> list:
        """自动获取策略类定义的所有变量名（排除基类属性和方法）"""
        基类属性 = set(dir(类_CTA策略模板))
        当前类属性 = set(dir(self.__class__))

        # 获取策略特有属性（排除基类属性和方法）
        策略特有属性 = []
        for 属性名 in 当前类属性 - 基类属性:
            # 排除方法、特殊属性和系统属性
            if (not callable(getattr(self.__class__, 属性名))
                    and not 属性名.startswith('__')
                    and 属性名 not in ["参数列表", "变量列表", "作者"]):
                策略特有属性.append(属性名)
        return 策略特有属性

    def 更新配置(self, 配置字典: dict) -> None:
        """更新策略参数配置"""
        for 参数名 in self.参数列表:
            if 参数名 in 配置字典:
                setattr(self, 参数名, 配置字典[参数名])

    @classmethod
    def 获取类参数(cls) -> dict:
        """获取策略类默认参数"""
        类参数字典 = {}
        for 参数名 in cls.参数列表:
            类参数字典[参数名] = getattr(cls, 参数名)
        return 类参数字典

    def 获取参数(self) -> dict:
        """获取策略参数"""
        参数字典 = {}
        for 参数名 in self.参数列表:
            参数字典[参数名] = getattr(self, 参数名)
        return 参数字典

    def 获取变量(self) -> dict:
        """获取策略变量"""
        变量字典 = {}
        for 变量名 in self.变量列表:
            变量字典[变量名] = getattr(self, 变量名)
        return 变量字典

    def 获取数据(self) -> dict:
        """获取策略完整数据"""
        return {
            "策略名称": self.策略名称,
            "合约_交易所": self.合约_交易所,
            "类名称": self.__class__.__name__,
            "作者": self.作者,
            "参数列表": self.获取参数(),
            "变量列表": self.获取变量(),
        }

    @虚拟方法
    def 初始化回调(self) -> None:
        """策略初始化完成回调"""
        pass

    @虚拟方法
    def 启动回调(self) -> None:
        """策略启动回调"""
        pass

    @虚拟方法
    def 停止回调(self) -> None:
        """策略停止回调"""
        pass

    @虚拟方法
    def 行情回调(self, 行情: 类_行情数据) -> None:
        """Tick行情更新"""
        pass

    @虚拟方法
    def K线回调(self, K线: 类_K线数据) -> None:
        """K线更新"""
        pass

    @虚拟方法
    def 成交回调(self, 成交: 类_成交数据) -> None:
        """成交更新"""
        pass

    @虚拟方法
    def 委托回调(self, 委托: 类_订单数据) -> None:
        """委托状态更新"""
        pass

    @虚拟方法
    def 停止单回调(self, 停止单: 类_停止单) -> None:
        """停止单更新"""
        pass

    def 买入开仓(
            self,
            价格: float,
            数量: float,
            停止单模式: bool = False,
            锁定模式: bool = False,
            净仓模式: bool = False
    ) -> list:
        """开多仓"""
        return self.发送委托(
            类_方向.做多,
            类_开平.开仓,
            价格,
            数量,
            停止单模式,
            锁定模式,
            净仓模式
        )

    def 卖出平仓(
            self,
            价格: float,
            数量: float,
            停止单模式: bool = False,
            锁定模式: bool = False,
            净仓模式: bool = False
    ) -> list:
        """平多仓"""
        return self.发送委托(
            类_方向.做空,
            类_开平.平仓,
            价格,
            数量,
            停止单模式,
            锁定模式,
            净仓模式
        )

    def 卖出开仓(
            self,
            价格: float,
            数量: float,
            停止单模式: bool = False,
            锁定模式: bool = False,
            净仓模式: bool = False
    ) -> list:
        """开空仓"""
        return self.发送委托(
            类_方向.做空,
            类_开平.开仓,
            价格,
            数量,
            停止单模式,
            锁定模式,
            净仓模式
        )

    def 买入平仓(
            self,
            价格: float,
            数量: float,
            停止单模式: bool = False,
            锁定模式: bool = False,
            净仓模式: bool = False
    ) -> list:
        """平空仓"""
        return self.发送委托(
            类_方向.做多,
            类_开平.平仓,
            价格,
            数量,
            停止单模式,
            锁定模式,
            净仓模式
        )

    def 发送委托(
            self,
            方向: 类_方向,
            开平: 类_开平,
            价格: float,
            数量: float,
            停止单: bool = False,
            锁定: bool = False,
            净仓: bool = False
    ) -> list:
        """发送委托核心方法"""
        if self.运行中:
            委托编号列表 = self.CTA引擎.发送订单(
                self, 方向, 开平, 价格, 数量, 停止单, 锁定, 净仓
            )
            self.记录日志(f'委托编号列表:{委托编号列表}')
            return 委托编号列表
        return []

    def 撤销委托(self, 委托编号: str) -> None:
        """撤销指定委托"""
        if self.运行中:
            self.CTA引擎.撤销订单(self, 委托编号)

    def 全部撤单(self) -> None:
        """撤销所有委托"""
        if self.运行中:
            self.CTA引擎.撤销全部订单(self)

    def 记录日志(self, 内容: str) -> None:
        """记录策略日志"""
        self.CTA引擎.记录日志(内容, self)

    def 获取引擎类型(self) -> 类_引擎类型:
        """获取引擎类型"""
        return self.CTA引擎.获取引擎类型()

    def 获取最小价位(self) -> float:
        """获取合约最小价格变动单位"""
        return self.CTA引擎.获取最小价位(self)

    def 获取合约乘数(self) -> int:
        """获取合约乘数"""
        return self.CTA引擎.获取合约乘数(self)

    def 加载K线(
            self,
            天数: int,
            周期: 类_周期 = 类_周期.一分钟,
            回调函数: Callable = None,
            使用数据库: bool = False
    ) -> None:
        """加载历史K线数据"""
        if not 回调函数:
            回调函数 = self.K线回调

        K线列表 = self.CTA引擎.加载K线数据(
            self.合约_交易所,
            天数,
            周期,
            回调函数,
            使用数据库
        )

        for K线 in K线列表:
            回调函数(K线)

    def 加载Tick(self, 天数: int) -> None:
        """加载历史Tick数据"""
        Tick列表 = self.CTA引擎.加载Tick数据(self.合约_交易所, 天数, self.行情回调)

        for Tick in Tick列表:
            self.行情回调(Tick)

    def 推送事件(self) -> None:
        """推送策略状态更新"""
        if self.已初始化:
            self.CTA引擎.推送策略事件(self)

    def 发送邮件(self, 内容: str) -> None:
        """发送策略邮件通知"""
        if self.已初始化:
            self.CTA引擎.发送邮件(内容, self)

    def 同步数据(self) -> None:
        """同步策略数据到存储"""
        if self.运行中:
            self.CTA引擎.同步策略数据(self)

class 类_CTA信号(ABC):
    """信号基类"""

    def __init__(self) -> None:
        self.信号当前仓位 = 0

    @虚拟方法
    def 行情回调(self, 行情: 类_行情数据) -> None:
        """Tick更新处理"""
        pass

    @虚拟方法
    def K线回调(self, K线: 类_K线数据) -> None:
        """K线更新处理"""
        pass

    def 设置信号当前仓位(self, 当前仓位: int) -> None:
        """更新信号当前仓位"""
        self.当前仓位 = 当前仓位

    def 获取信号当前仓位(self) -> int:
        """获取信号当前当前仓位"""
        return self.信号当前仓位


class 类_目标仓位模板(类_CTA策略模板):
    """目标仓位策略模板"""

    最小变动单位 = 1

    最新行情: 类_行情数据 = None
    最新K线: 类_K线数据 = None
    目标仓位 = 0

    def __init__(self, CTA引擎, 策略名称, 合约_交易所, 配置) -> None:
        super().__init__(CTA引擎, 策略名称, 合约_交易所, 配置)

        self.目标仓位: int = 0
        self.活跃委托列表: list = []
        self.待撤单列表: list = []

        self.变量列表.append("目标仓位")

    @虚拟方法
    def 行情回调(self, 行情: 类_行情数据) -> None:
        """记录最新行情"""
        self.最新行情 = 行情

    @虚拟方法
    def K线回调(self, K线: 类_K线数据) -> None:
        """记录最新K线"""
        self.最新K线 = K线

    @虚拟方法
    def 委托回调(self, 委托: 类_订单数据) -> None:
        """处理委托更新"""
        委托编号 = 委托.网关_订单编号

        if not 委托.是否活跃():
            if 委托编号 in self.活跃委托列表:
                self.活跃委托列表.remove(委托编号)
            if 委托编号 in self.待撤单列表:
                self.待撤单列表.remove(委托编号)

    def 检查委托完成(self) -> bool:
        """检查所有委托是否完成"""
        return not bool(self.活跃委托列表)

    def 设置目标仓位(self, 目标仓位: int) -> None:
        """更新目标仓位并触发交易"""
        self.目标仓位 = 目标仓位
        self.执行交易()

    def 执行交易(self) -> None:
        """执行仓位调整"""
        if not self.检查委托完成():
            self.撤销旧单()
        else:
            self.发送新单()

    def 撤销旧单(self) -> None:
        """撤销所有未完成委托"""
        for 委托编号 in self.活跃委托列表:
            if 委托编号 not in self.待撤单列表:
                self.撤销订单(委托编号)
                self.待撤单列表.append(委托编号)

    def 发送新单(self) -> None:
        """根据目标仓位发送新委托"""
        仓位变化 = self.目标仓位 - self.当前仓位
        if not 仓位变化:
            return

        # 计算委托价格
        多头价格 = 0
        空头价格 = 0

        if self.最新行情:
            if 仓位变化 > 0:
                多头价格 = self.最新行情.卖一价 + self.最小变动单位
                if self.最新行情.涨停价:
                    多头价格 = min(多头价格, self.最新行情.涨停价)
            else:
                空头价格 = self.最新行情.买一价 - self.最小变动单位
                if self.最新行情.跌停价:
                    空头价格 = max(空头价格, self.最新行情.跌停价)
        else:
            if 仓位变化 > 0:
                多头价格 = self.最新K线.收盘价 + self.最小变动单位
            else:
                空头价格 = self.最新K线.收盘价 - self.最小变动单位

        # 回测模式处理
        if self.获取引擎类型() == 类_引擎类型.回测模式:
            if 仓位变化 > 0:
                委托列表 = self.买入(多头价格, abs(仓位变化))
            else:
                委托列表 = self.做空(空头价格, abs(仓位变化))
            self.活跃委托列表.extend(委托列表)
        else:
            if self.活跃委托列表:
                return

            # 实盘模式仓位调整
            if 仓位变化 > 0:
                if self.当前仓位 < 0:
                    平仓量 = min(abs(仓位变化), abs(self.当前仓位))
                    委托列表 = self.平空(多头价格, 平仓量)
                else:
                    委托列表 = self.买入(多头价格, abs(仓位变化))
            else:
                if self.当前仓位 > 0:
                    平仓量 = min(abs(仓位变化), self.当前仓位)
                    委托列表 = self.卖出(空头价格, 平仓量)
                else:
                    委托列表 = self.做空(空头价格, abs(仓位变化))
            self.活跃委托列表.extend(委托列表)