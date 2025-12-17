"""定义CTA策略应用的常量和对象"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict
from xmpy.包_交易核心.模块_常数 import 类_方向, 类_开平, 类_周期
from .包_国际化 import _

# 应用常量
应用名称 = "CTA策略"
停止单前缀 = "STOP"

class 类_停止单状态(Enum):
    """停止单状态枚举"""
    等待中 = _("等待中")
    已撤销 = _("已撤销")
    已触发 = _("已触发")

class 类_引擎类型(Enum):
    """策略引擎类型枚举"""
    实盘模式 = _("实盘")
    回测模式 = _("回测")

class 类_回测模式(Enum):
    """回测数据模式枚举"""
    K线模式 = 1
    Tick模式 = 2

@dataclass
class 类_停止单:
    """停止单数据结构"""
    合约_交易所: str
    方向: 类_方向
    开平: 类_开平
    价格: float
    数量: float
    停止单编号: str
    策略名称: str
    时间戳: datetime
    锁定模式: bool = False
    净仓模式: bool = False
    订单编号列表: list = field(default_factory=list)
    状态: 类_停止单状态 = 类_停止单状态.等待中

# 事件类型定义
事件类型_CTA日志 = "eCtaLog"
事件类型_CTA策略 = "eCtaStrategy"
事件类型_CTA停止单 = "eCtaStopOrder"

# 周期时间差映射
周期映射表: Dict[类_周期, timedelta] = {
    类_周期.Tick级: timedelta(milliseconds=1),
    类_周期.一分钟: timedelta(minutes=1),
    类_周期.一小时: timedelta(hours=1),
    类_周期.日线: timedelta(days=1),
}

# 新添加
class 类_条件类型(Enum):
    """ 条件单的条件 """
    大于 = ">"
    小于 = "<"
    大于等于 = ">="
    小于等于 = "<="

class 类_执行价格类型(Enum):
    """ 执行价格 """
    设定价 = "设定价"
    市场价 = "市场价"
    极限价 = "极限价"

class 类_条件单状态(Enum):
    """ 条件单状态 """
    等待中 = "等待中"
    已撤销 = "已撤销"
    已触发 = "已触发"