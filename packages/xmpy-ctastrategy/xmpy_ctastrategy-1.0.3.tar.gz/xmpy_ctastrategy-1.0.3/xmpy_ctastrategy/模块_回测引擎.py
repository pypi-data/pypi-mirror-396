import time

from collections import defaultdict
from datetime import (
    date as Date,
    datetime,
    timedelta
)
from typing import cast, Any
from collections.abc import Callable
from functools import lru_cache, partial
import traceback

import numpy as np
from pandas import DataFrame, Series
from pandas.core.window import ExponentialMovingWindow
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import multiprocessing as mp
from tqdm import tqdm
from time import perf_counter

from xmpy.包_交易核心.模块_常数 import (
    类_方向,
    类_周期,
    类_交易所,
    类_开平,
    类_状态
)

from xmpy.包_交易核心.模块_基础数据库 import 类_基础数据库, 获取数据库, 数据库时区
from xmpy.包_交易核心.模块_对象 import (
    类_订单数据,
    类_成交数据,
    类_K线数据,
    类_行情数据,
)
from xmpy.包_交易核心.模块_工具 import 提取合约代码, 四舍五入到指定值
from xmpy.包_交易核心.模块_优化 import (
    类_优化设置,
    检查优化设置
)

from .模块_基础 import 类_回测模式,类_引擎类型,停止单前缀,类_停止单,类_停止单状态,周期映射表
from .模块_模板 import 类_CTA策略模板

class 类_回测引擎:
    """"""

    引擎类型: 类_引擎类型 = 类_引擎类型.回测模式
    网关名称: str = "回测"

    def __init__(self) -> None:
        """"""
        self.合约_交易所: str = ""
        self.代码: str = ""   # 如 TA2509
        self.交易所: 类_交易所
        self.开始时间: datetime
        self.结束时间: datetime
        self.手续费: float = 0
        self.滑点: float = 0
        self.合约乘数: float = 1
        self.最小变动价位: float = 0
        self.初始资金: int = 5_000_000
        self.无风险利率: float = 0
        self.年交易日数: int = 240
        self.半衰期: int = 120
        self.模式: 类_回测模式 = 类_回测模式.K线模式

        self.策略类: type[类_CTA策略模板]
        self.策略: 类_CTA策略模板
        self.行情: 类_行情数据
        self.K线: 类_K线数据
        self.当前时间: datetime = datetime(1970, 1, 1)

        self.周期: 类_周期
        self.天数: int = 0
        self.回调函数: Callable
        self.历史数据: list = []

        self.停止单计数: int = 0
        self.所有停止单: dict[str, 类_停止单] = {}
        self.活跃停止单: dict[str, 类_停止单] = {}

        self.限价单计数: int = 0
        self.所有限价单: dict[str, 类_订单数据] = {}
        self.活跃限价单: dict[str, 类_订单数据] = {}

        self.成交计数: int = 0
        self.所有成交: dict[str, 类_成交数据] = {}

        self.日志: list = []

        self.每日结果: dict[Date, 类_每日结果] = {}
        self.每日数据框: DataFrame

    def 清空数据(self) -> None:
        """
        清空上次回测的所有数据
        """
        self.停止单计数 = 0
        self.所有停止单.clear()
        self.活跃停止单.clear()

        self.限价单计数 = 0
        self.所有限价单.clear()
        self.活跃限价单.clear()

        self.成交计数 = 0
        self.所有成交.clear()

        self.日志.clear()
        self.每日结果.clear()

    def 设置参数(
        self,
        合约_交易所: str,
        周期: 类_周期,
        开始时间: datetime,
        手续费: float,
        滑点: float,
        合约乘数: float,
        最小价位: float,
        初始资金: int = 0,
        结束时间: datetime | None = None,
        模式: 类_回测模式 = 类_回测模式.K线模式,
        无风险利率: float = 0,
        年交易日数: int = 240,
        半衰期: int = 120
    ) -> None:
        """"""
        self.模式 = 模式
        self.合约_交易所 = 合约_交易所
        self.周期 = 类_周期(周期)
        self.手续费 = 手续费
        self.滑点 = 滑点
        self.合约乘数 = 合约乘数
        self.最小变动价位 = 最小价位
        self.开始时间 = 开始时间

        self.代码, self.交易所 = 提取合约代码(self.合约_交易所)

        self.初始资金 = 初始资金

        if not 结束时间:
            结束时间 = datetime.now()
        self.结束时间 = 结束时间.replace(hour=23, minute=59, second=59)

        self.模式 = 模式
        self.无风险利率 = 无风险利率
        self.年交易日数 = 年交易日数
        self.半衰期 = 半衰期

    def 添加策略(self, 策略类: type[类_CTA策略模板], 参数设置: dict) -> None:
        """"""
        self.策略类 = 策略类
        self.策略 = 策略类(
            self, 策略类.__name__, self.合约_交易所, 参数设置
        )

    def 加载数据(self) -> None:
        """"""
        self.输出("开始加载历史数据")

        if not self.结束时间:
            self.结束时间 = datetime.now()

        if self.开始时间 >= self.结束时间:
            self.输出("起始日期必须小于结束日期")
            return

        self.历史数据.clear()       # 清除之前加载的历史数据

        # 每次加载30天数据并允许更新进度
        总天数: int = (self.结束时间 - self.开始时间).days
        总天数: int = max(int(总天数), 1)
        进度天数: int = max(int(总天数 / 10), 1)
        进度时间差: timedelta = timedelta(days=进度天数)
        周期时间差: timedelta = 周期映射表[self.周期]

        开始时间: datetime = self.开始时间
        结束时间: datetime = self.结束时间
        进度: float = 0

        while 开始时间 < self.结束时间:
            进度条: str = "#" * int(进度 * 10 + 1)
            self.输出(f"加载进度：{进度条} [{进度:.0%}]")

            结束时间 = min(结束时间, self.结束时间)  # 确保结束时间在设定范围内

            if self.模式 == 类_回测模式.K线模式:
                数据: list[类_K线数据] = 加载K线数据(
                    self.代码,
                    self.交易所,
                    self.周期,
                    开始时间,
                    结束时间
                )
            else:
                数据 = 加载Tick数据(
                    self.代码,
                    self.交易所,
                    开始时间,
                    结束时间
                )

            self.历史数据.extend(数据)

            进度 += 进度天数 / 总天数
            进度 = min(进度, 1)

            开始时间 = 结束时间 + 周期时间差
            结束时间 += 进度时间差

        self.输出(f"历史数据加载完成，数据量：{len(self.历史数据)}")

    def 运行回测(self) -> None:
        """"""
        if self.模式 == 类_回测模式.K线模式:
            函数: Callable[[Any], None] = self.新K线
        else:
            函数 = self.新行情

        self.策略.初始化回调()
        self.策略.已初始化 = True
        self.输出("策略初始化完成")

        self.策略.启动回调()
        self.策略.运行中 = True
        self.输出("开始回放历史数据")

        总数量: int = len(self.历史数据)
        批次大小: int = max(int(总数量 / 10), 1)

        for 索引, i in enumerate(range(0, 总数量, 批次大小)):
            批次数据: list = self.历史数据[i: i + 批次大小]
            for 数据 in 批次数据:
                try:
                    函数(数据)
                except Exception:
                    self.输出("触发异常，回测终止")
                    self.输出(traceback.format_exc())
                    return

            进度 = min(索引 / 10, 1)
            进度条: str = "=" * (索引 + 1)
            self.输出(f"回放进度：{进度条} [{进度:.0%}]")

        self.策略.停止回调()
        self.输出("历史数据回放结束")

    def 计算结果(self) -> DataFrame:
        """"""
        self.输出("开始计算逐日盯市盈亏")

        if not self.所有成交:
            self.输出("回测成交记录为空")

        # 将成交数据添加到每日结果中
        for 成交 in self.所有成交.values():
            日期: Date = 成交.时间戳.date()
            每日结果: 类_每日结果 = self.每日结果[日期]
            每日结果.添加成交(成交)

        # 通过迭代计算每日结果
        前收盘价: float = 0
        起始仓位: float = 0

        for 每日结果 in self.每日结果.values():
            每日结果.计算盈亏(
                前收盘价,
                起始仓位,
                self.合约乘数,
                self.手续费,
                self.滑点
            )

            前收盘价 = 每日结果.收盘价
            起始仓位 = 每日结果.结束仓位

        # 生成数据框
        结果字典: defaultdict = defaultdict(list)

        for 每日结果 in self.每日结果.values():
            for 键, 值 in 每日结果.__dict__.items():
                结果字典[键].append(值)

        self.每日数据框 = DataFrame.from_dict(结果字典).set_index("日期")

        self.输出("逐日盯市盈亏计算完成")
        return self.每日数据框

    def 计算统计指标(
        self,
        数据框: DataFrame | None = None,
        是否打印结果: bool = True
    ) -> dict:
        """"""
        self.输出("开始计算策略统计指标")

        # 检查外部输入的DataFrame
        if 数据框 is None:
            if self.每日数据框.empty:
                self.输出("回测结果为空，无法计算绩效统计指标")
                return {}

            数据框 = self.每日数据框

        # 初始化所有统计指标的默认值
        起始日期: str = ""
        结束日期: str = ""
        总交易日数: int = 0
        盈利天数: int = 0
        亏损天数: int = 0
        结束资金: float = 0
        最大回撤: float = 0
        百分比最大回撤: float = 0
        最大回撤天数: int = 0
        总净盈亏: float = 0
        日均盈亏: float = 0
        总手续费: float = 0
        日均手续费: float = 0
        总滑点: float = 0
        日均滑点: float = 0
        总成交额: float = 0
        日均成交额: float = 0
        总成交笔数: int = 0
        日均成交笔数: float = 0
        总收益率: float = 0
        年化收益率: float = 0
        日均收益率: float = 0
        收益标准差: float = 0
        夏普比率: float = 0
        指数加权夏普: float = 0
        收益回撤比: float = 0

        # 检查资金是否始终为正
        资金为正: bool = False

        if 数据框 is not None:
            # 计算资金相关的时间序列数据
            数据框["资金"] = 数据框["净盈亏"].cumsum() + self.初始资金

            # 当资金低于0时，将日收益率设为0
            前资金: Series = 数据框["资金"].shift(1)
            前资金.iloc[0] = self.初始资金
            x = 数据框["资金"] / 前资金
            x[x <= 0] = np.nan
            数据框["收益率"] = np.log(x).fillna(0)

            数据框["最高水位"] = 数据框["资金"].rolling(min_periods=1, window=len(数据框), center=False).max()
            数据框["回撤"] = 数据框["资金"] - 数据框["最高水位"]
            数据框["回撤百分比"] = 数据框["回撤"] / 数据框["最高水位"] * 100

            # 所有资金值必须为正
            资金为正 = (数据框["资金"] > 0).all()
            if not 资金为正:
                self.输出("回测中出现爆仓（资金小于等于0），无法计算策略统计指标")

        # 计算统计值
        if 资金为正:
            # 计算统计值
            起始日期 = 数据框.index[0]
            结束日期 = 数据框.index[-1]

            总交易日数 = len(数据框)
            盈利天数 = len(数据框[数据框["净盈亏"] > 0])
            亏损天数 = len(数据框[数据框["净盈亏"] < 0])

            结束资金 = 数据框["资金"].iloc[-1]
            最大回撤 = 数据框["回撤"].min()
            百分比最大回撤 = 数据框["回撤百分比"].min()
            最大回撤结束日期 = 数据框["回撤"].idxmin()

            if isinstance(最大回撤结束日期, Date):
                最大回撤开始日期 = 数据框["资金"][:最大回撤结束日期].idxmax()      # type: ignore
                最大回撤天数 = (最大回撤结束日期 - 最大回撤开始日期).days
            else:
                最大回撤天数 = 0

            总净盈亏 = 数据框["净盈亏"].sum()
            日均盈亏 = 总净盈亏 / 总交易日数

            总手续费 = 数据框["手续费"].sum()
            日均手续费 = 总手续费 / 总交易日数

            总滑点 = 数据框["滑点"].sum()
            日均滑点 = 总滑点 / 总交易日数

            总成交额 = 数据框["成交额"].sum()
            日均成交额 = 总成交额 / 总交易日数

            总成交笔数 = 数据框["成交笔数"].sum()
            日均成交笔数 = 总成交笔数 / 总交易日数

            总收益率 = (结束资金 / self.初始资金 - 1) * 100
            年化收益率 = 总收益率 / 总交易日数 * self.年交易日数
            日均收益率 = 数据框["收益率"].mean() * 100
            收益标准差 = 数据框["收益率"].std() * 100

            if 收益标准差:
                日无风险利率: float = self.无风险利率 / np.sqrt(self.年交易日数)
                夏普比率 = (日均收益率 - 日无风险利率) / 收益标准差 * np.sqrt(self.年交易日数)

                指数加权窗口: ExponentialMovingWindow = 数据框["收益率"].ewm(halflife=self.半衰期)
                指数加权均值: Series = 指数加权窗口.mean() * 100
                指数加权标准差: Series = 指数加权窗口.std() * 100
                指数加权夏普 = ((指数加权均值 - 日无风险利率) / 指数加权标准差).iloc[-1] * np.sqrt(self.年交易日数)
            else:
                夏普比率 = 0
                指数加权夏普 = 0

            if 百分比最大回撤:
                收益回撤比 = -总收益率 / 百分比最大回撤
            else:
                收益回撤比 = 0

        # 输出
        if 是否打印结果:
            self.输出("-" * 30)
            self.输出(f"首个交易日：\t{起始日期}")
            self.输出(f"最后交易日：\t{结束日期}")

            self.输出(f"总交易日：\t{总交易日数}")
            self.输出(f"盈利交易日：\t{盈利天数}")
            self.输出(f"亏损交易日：\t{亏损天数}")

            self.输出(f"起始资金：\t{self.初始资金:,.2f}")
            self.输出(f"结束资金：\t{结束资金:,.2f}")

            self.输出(f"总收益率：\t{总收益率:,.2f}%")
            self.输出(f"年化收益：\t{年化收益率:,.2f}%")
            self.输出(f"最大回撤: \t{最大回撤:,.2f}")
            self.输出(f"百分比最大回撤: {百分比最大回撤:,.2f}%")
            self.输出(f"最大回撤天数: \t{最大回撤天数}")

            self.输出(f"总盈亏：\t{总净盈亏:,.2f}")
            self.输出(f"总手续费：\t{总手续费:,.2f}")
            self.输出(f"总滑点：\t{总滑点:,.2f}")
            self.输出(f"总成交金额：\t{总成交额:,.2f}")
            self.输出(f"总成交笔数：\t{总成交笔数}")

            self.输出(f"日均盈亏：\t{日均盈亏:,.2f}")
            self.输出(f"日均手续费：\t{日均手续费:,.2f}")
            self.输出(f"日均滑点：\t{日均滑点:,.2f}")
            self.输出(f"日均成交金额：\t{日均成交额:,.2f}")
            self.输出(f"日均成交笔数：\t{日均成交笔数}")

            self.输出(f"日均收益率：\t{日均收益率:,.2f}%")
            self.输出(f"收益标准差：\t{收益标准差:,.2f}%")
            self.输出(f"夏普比率：\t{夏普比率:,.2f}")
            self.输出(f"指数加权夏普：\t{指数加权夏普:,.2f}")
            self.输出(f"收益回撤比：\t{收益回撤比:,.2f}")

        统计指标: dict = {
            "起始日期": 起始日期,
            "结束日期": 结束日期,
            "总交易日数": 总交易日数,
            "盈利天数": 盈利天数,
            "亏损天数": 亏损天数,
            "初始资金": self.初始资金,
            "结束资金": 结束资金,
            "最大回撤": 最大回撤,
            "百分比最大回撤": 百分比最大回撤,
            "最大回撤天数": 最大回撤天数,
            "总净盈亏": 总净盈亏,
            "日均盈亏": 日均盈亏,
            "总手续费": 总手续费,
            "日均手续费": 日均手续费,
            "总滑点": 总滑点,
            "日均滑点": 日均滑点,
            "总成交额": 总成交额,
            "日均成交额": 日均成交额,
            "总成交笔数": 总成交笔数,
            "日均成交笔数": 日均成交笔数,
            "总收益率": 总收益率,
            "年化收益率": 年化收益率,
            "日均收益率": 日均收益率,
            "收益标准差": 收益标准差,
            "夏普比率": 夏普比率,
            "指数加权夏普": 指数加权夏普,
            "收益回撤比": 收益回撤比,
        }

        # 过滤潜在的无限值错误
        for 键, 值 in 统计指标.items():
            if 值 in (np.inf, -np.inf):
                值 = 0
            统计指标[键] = np.nan_to_num(值)

        self.输出("策略统计指标计算完成")
        return 统计指标

    def 显示图表(self, 数据框: DataFrame | None = None) -> go.Figure:
        """"""
        # 检查外部输入的DataFrame
        if 数据框 is None:
            数据框 = self.每日数据框

        # 检查初始化的DataFrame
        if 数据框 is None:
            return

        图表 = make_subplots(
            rows=4,
            cols=1,
            subplot_titles=["资金曲线", "回撤", "每日盈亏", "盈亏分布"],
            vertical_spacing=0.06
        )

        资金曲线 = go.Scatter(
            x=数据框.index,
            y=数据框["资金"],
            mode="lines",
            name="资金"
        )

        回撤图 = go.Scatter(
            x=数据框.index,
            y=数据框["回撤"],
            fillcolor="red",
            fill='tozeroy',
            mode="lines",
            name="回撤"
        )

        盈亏柱状图 = go.Bar(y=数据框["净盈亏"], name="每日盈亏")
        盈亏直方图 = go.Histogram(x=数据框["净盈亏"], nbinsx=100, name="天数")

        图表.add_trace(资金曲线, row=1, col=1)
        图表.add_trace(回撤图, row=2, col=1)
        图表.add_trace(盈亏柱状图, row=3, col=1)
        图表.add_trace(盈亏直方图, row=4, col=1)

        图表.update_layout(height=1000, width=1000)
        # 图表.show()
        return 图表

    def 更新每日收盘价(self, 价格: float) -> None:
        """"""
        日期: Date = self.当前时间.date()

        每日结果: 类_每日结果 | None = self.每日结果.get(日期, None)
        if 每日结果:
            每日结果.收盘价 = 价格
        else:
            self.每日结果[日期] = 类_每日结果(日期, 价格)

    def 新K线(self, K线: 类_K线数据) -> None:
        """"""
        self.K线 = K线
        self.当前时间 = K线.时间戳

        self.撮合限价单()
        self.撮合停止单()
        self.策略.K线回调(K线)

        self.更新每日收盘价(K线.收盘价)

    def 新行情(self, 行情: 类_行情数据) -> None:
        """"""
        self.行情 = 行情
        self.当前时间 = 行情.时间戳

        self.撮合限价单()
        self.撮合停止单()
        self.策略.行情回调(行情)

        self.更新每日收盘价(行情.最新价)

    def 撮合限价单(self) -> None:
        """
        使用最新的K线/行情数据撮合限价单
        """
        if self.模式 == 类_回测模式.K线模式:
            多头撮合价 = self.K线.最低价
            空头撮合价 = self.K线.最高价
            多头最优价 = self.K线.开盘价
            空头最优价 = self.K线.开盘价
        else:
            多头撮合价 = self.行情.卖一价
            空头撮合价 = self.行情.买一价
            多头最优价 = 多头撮合价
            空头最优价 = 空头撮合价

        for 订单 in list(self.活跃限价单.values()):
            # 推送状态为"未成交"(等待中)的订单更新
            if 订单.状态 == 类_状态.提交中:
                订单.状态 = 类_状态.未成交
                self.策略.委托回调(订单)

            # 检查限价单是否可以成交
            多头撮合: bool = (
                订单.方向 == 类_方向.做多
                and 订单.价格 >= 多头撮合价
                and 多头撮合价 > 0
            )

            空头撮合: bool = (
                订单.方向 == 类_方向.做空
                and 订单.价格 <= 空头撮合价
                and 空头撮合价 > 0
            )

            if not 多头撮合 and not 空头撮合:
                continue

            # 推送状态为"全部成交"的订单更新
            订单.已成交 = 订单.数量
            订单.状态 = 类_状态.全部成交
            self.策略.委托回调(订单)

            if 订单.网关_订单编号 in self.活跃限价单:
                self.活跃限价单.pop(订单.网关_订单编号)

            # 推送成交更新
            self.成交计数 += 1

            if 多头撮合:
                成交价 = min(订单.价格, 多头最优价)
            else:
                成交价 = max(订单.价格, 空头最优价)

            成交: 类_成交数据 = 类_成交数据(
                代码=订单.代码,
                交易所=订单.交易所,
                订单编号=订单.订单编号,
                成交编号=str(self.成交计数),
                方向=订单.方向,
                开平=订单.开平,
                价格=成交价,
                数量=订单.数量,
                时间戳=self.当前时间,
                网关名称=self.网关名称,
            )

            可成交 = True

            if 成交.方向 == 类_方向.做多 and 成交.开平 == 类_开平.开仓:
                self.策略.多头仓位 += 成交.数量
            elif 成交.方向 == 类_方向.做空 and 成交.开平 == 类_开平.开仓:
                self.策略.空头仓位 += 成交.数量

            elif 成交.方向 == 类_方向.做空 and 成交.开平.value in ["平", "平今", "平昨"]:
                # 检查平仓后仓位是否会出现负数
                if self.策略.多头仓位 >= 成交.数量:
                    self.策略.多头仓位 -= 成交.数量
                else:
                    print(f'多头仓位发生问题：{成交}')
                    可成交 = False
            elif 成交.方向 == 类_方向.做多 and 成交.开平.value in ["平", "平今", "平昨"]:
                if self.策略.空头仓位 >= 成交.数量:
                    self.策略.空头仓位 -= 成交.数量
                else:
                    print(f'空头仓位发生问题：{成交}')
                    可成交 = False

            if not 可成交:
                continue

            self.策略.成交回调(成交)

            self.所有成交[成交.网关_成交编号] = 成交

    def 撮合停止单(self) -> None:
        """
        使用最新的K线/行情数据撮合停止单
        """
        if self.模式 == 类_回测模式.K线模式:
            多头撮合价 = self.K线.最高价
            空头撮合价 = self.K线.最低价
            多头最优价 = self.K线.开盘价
            空头最优价 = self.K线.开盘价
        else:
            多头撮合价 = self.行情.最新价
            空头撮合价 = self.行情.最新价
            多头最优价 = 多头撮合价
            空头最优价 = 空头撮合价

        for 停止单 in list(self.活跃停止单.values()):
            # 检查停止单是否可以触发
            多头触发: bool = (
                停止单.方向 == 类_方向.做多
                and 停止单.价格 <= 多头撮合价
            )

            空头触发: bool = (
                停止单.方向 == 类_方向.做空
                and 停止单.价格 >= 空头撮合价
            )

            if not 多头触发 and not 空头触发:
                continue

            # 创建订单数据
            self.限价单计数 += 1

            订单: 类_订单数据 = 类_订单数据(
                代码=self.代码,
                交易所=self.交易所,
                订单编号=str(self.限价单计数),
                方向=停止单.方向,
                开平=停止单.开平,
                价格=停止单.价格,
                数量=停止单.数量,
                已成交=停止单.数量,
                状态=类_状态.全部成交,
                时间戳=self.当前时间,
                网关名称=self.网关名称
            )

            self.所有限价单[订单.网关_订单编号] = 订单

            # 创建成交数据
            if 多头触发:
                成交价 = max(停止单.价格, 多头最优价)
            else:
                成交价 = min(停止单.价格, 空头最优价)

            self.成交计数 += 1

            成交: 类_成交数据 = 类_成交数据(
                代码=订单.代码,
                交易所=订单.交易所,
                订单编号=订单.订单编号,
                成交编号=str(self.成交计数),
                方向=订单.方向,
                开平=订单.开平,
                价格=成交价,
                数量=订单.数量,
                时间戳=self.当前时间,
                网关名称=self.网关名称,
            )

            self.所有成交[成交.网关_成交编号] = 成交

            # 更新停止单
            停止单.订单编号列表.append(订单.网关_订单编号)
            停止单.状态 = 类_条件单状态.已触发

            if 停止单.停止单编号 in self.活跃停止单:
                self.活跃停止单.pop(停止单.停止单编号)

            # 推送更新到策略
            self.策略.停止单回调(停止单)
            self.策略.委托回调(订单)

            可成交 = True
            
            if 成交.方向 == 类_方向.做多 and 成交.开平 == 类_开平.开仓:
                self.策略.多头仓位 += 成交.数量
            elif 成交.方向 == 类_方向.做空 and 成交.开平 == 类_开平.开仓:
                self.策略.空头仓位 += 成交.数量
            # 平仓
            elif 成交.方向 == 类_方向.做空 and 成交.开平.value in ["平", "平今", "平昨"]:
                # 检查平仓后仓位是否会出现负数
                if self.策略.多头仓位 >= 成交.数量:
                    self.策略.多头仓位 -= 成交.数量
                else:
                    print(f'多头仓位发生问题：{成交}')
                    可成交 = False
            elif 成交.方向 == 类_方向.做多 and 成交.开平.value in ["平", "平今", "平昨"]:
                if self.策略.空头仓位 >= 成交.数量:
                    self.策略.空头仓位 -= 成交.数量
                else:
                    print(f'空头仓位发生问题：{成交}')
                    可成交 = False

            if not 可成交:
                continue
            self.策略.成交回调(成交)

    def 加载K线(
        self,
        合约_交易所: str,
        天数: int,
        周期: 类_周期,
        回调函数: Callable,
        使用数据库: bool
    ) -> list[类_K线数据]:
        """"""
        self.回调函数 = 回调函数

        初始结束时间 = self.开始时间 - 周期映射表[周期]
        初始开始时间 = self.开始时间 - timedelta(days=天数)

        代码, 交易所 = 提取合约代码(合约_交易所)

        K线列表: list[类_K线数据] = 加载K线数据(
            代码,
            交易所,
            周期,
            初始开始时间,
            初始结束时间
        )

        return K线列表

    def 加载行情(self, 合约_交易所: str, 天数: int, 回调函数: Callable) -> list[类_行情数据]:
        """"""
        self.回调函数 = 回调函数

        初始结束时间 = self.开始时间 - timedelta(seconds=1)
        初始开始时间 = self.开始时间 - timedelta(days=天数)

        代码, 交易所 = 提取合约代码(合约_交易所)

        行情列表: list[类_行情数据] = 加载Tick数据(
            代码,
            交易所,
            初始开始时间,
            初始结束时间
        )

        return 行情列表

    def 发送订单(
        self,
        策略实例: 类_CTA策略模板,
        方向: 类_方向,
        开平: 类_开平,
        价格: float,
        数量: float,
        停止单: bool,
        锁定: bool,
        净仓: bool
    ) -> list:
        """"""
        价格 = 四舍五入到指定值(价格, self.最小变动价位)
        if 停止单:
            订单号: str = self.发送停止单(方向, 开平, 价格, 数量)
        else:
            订单号 = self.发送限价单(方向, 开平, 价格, 数量)
        return [订单号]

    def 发送停止单(
        self,
        方向: 类_方向,
        开平: 类_开平,
        价格: float,
        数量: float
    ) -> str:
        """"""
        self.停止单计数 += 1

        停止单实例: 类_停止单 = 类_停止单(
            合约_交易所=self.合约_交易所,
            方向=方向,
            开平=开平,
            价格=价格,
            数量=数量,
            时间戳=self.当前时间,
            订单编号列表=f"{停止单前缀}.{self.停止单计数}",
            策略名称=self.策略.策略名称,
        )

        self.活跃停止单[停止单实例.停止单编号] = 停止单实例
        self.所有停止单[停止单实例.停止单编号] = 停止单实例

        return 停止单实例.停止单编号

    def 发送限价单(
        self,
        方向: 类_方向,
        开平: 类_开平,
        价格: float,
        数量: float
    ) -> str:
        """"""
        self.限价单计数 += 1

        订单: 类_订单数据 = 类_订单数据(
            代码=self.代码,
            交易所=self.交易所,
            订单编号=str(self.限价单计数),
            方向=方向,
            开平=开平,
            价格=价格,
            数量=数量,
            已成交=数量,
            状态=类_状态.提交中,
            时间戳=self.当前时间,
            网关名称=self.网关名称
        )

        self.活跃限价单[订单.网关_订单编号] = 订单
        self.所有限价单[订单.网关_订单编号] = 订单

        return 订单.网关_订单编号     # type: ignore

    def 撤单(self, 策略实例: 类_CTA策略模板, 订单号: str) -> None:
        """
        通过订单号取消订单
        """
        if 订单号.startswith(停止单前缀):
            self.取消停止单(策略实例, 订单号)
        else:
            self.取消限价单(策略实例, 订单号)

    def 取消停止单(self, 策略实例: 类_CTA策略模板, 订单号: str) -> None:
        """"""
        if 订单号 not in self.活跃停止单:
            return
        停止单实例: 类_停止单 = self.活跃停止单.pop(订单号)

        停止单实例.状态 = 类_停止单状态.已撤销
        self.策略.停止单回调(停止单实例)

    def 取消限价单(self, 策略实例: 类_CTA策略模板, 订单号: str) -> None:
        """"""
        if 订单号 not in self.活跃限价单:
            return
        订单: 类_订单数据 = self.活跃限价单.pop(订单号)

        订单.状态 = 类_状态.已撤销
        self.策略.委托回调(订单)

    def 撤销全部订单(self, 策略实例: 类_CTA策略模板) -> None:
        """
        取消所有订单，包括限价单和停止单
        """
        订单号列表: list = list(self.活跃限价单.keys())
        for 订单号 in 订单号列表:
            self.取消限价单(策略实例, 订单号)

        停止单号列表: list = list(self.活跃停止单.keys())
        for 订单号 in 停止单号列表:
            self.取消停止单(策略实例, 订单号)

    def 记录日志(self, 消息: str, 策略: 类_CTA策略模板 | None = None) -> None:
        """
        写入日志消息
        """
        消息 = f"{self.当前时间}\t{消息}"
        self.日志.append(消息)

    def 发送邮件(self, 消息: str, 策略: 类_CTA策略模板 | None = None) -> None:
        """
        发送邮件到默认接收者
        """
        pass

    def 同步策略数据(self, 策略: 类_CTA策略模板) -> None:
        """
        将策略数据同步到json文件
        """
        pass

    def 获取引擎类型(self) -> 类_引擎类型:
        """
        返回引擎类型
        """
        return self.引擎类型

    def 获取最小价位(self, 策略: 类_CTA策略模板) -> float:
        """
        返回合约最小价位
        """
        return self.最小变动价位

    def 获取合约乘数(self, 策略: 类_CTA策略模板) -> float:
        """
        返回合约乘数
        """
        return self.合约乘数

    def 推送策略事件(self, 策略: 类_CTA策略模板) -> None:
        """
        推送事件更新策略状态
        """
        pass

    def 输出(self, 消息: str) -> None:
        """
        输出回测引擎消息
        """
        print(f"{datetime.now()}\t{消息}")

    def 获取所有成交(self) -> list:
        """
        返回当前回测结果的所有成交数据
        """
        return list(self.所有成交.values())

    def 获取所有订单(self) -> list:
        """
        返回当前回测结果的所有限价单数据
        """
        return list(self.所有限价单.values())

    def 获取所有每日结果(self) -> list:
        """
        返回所有每日结果数据
        """
        return list(self.每日结果.values())


class 类_每日结果:
    """"""

    def __init__(self, 日期: Date, 收盘价: float) -> None:
        """"""
        self.日期: Date = 日期
        self.收盘价: float = 收盘价
        self.前收盘价: float = 0

        self.成交列表: list[类_成交数据] = []
        self.成交笔数: int = 0

        self.起始仓位: float = 0
        self.结束仓位: float = 0

        self.空单价格列表 = []
        self.多单价格列表 = []

        self.空单持仓均价 = 0
        self.多单持仓均价 = 0

        self.空单仓位 = []
        self.多单仓位 = []

        self.成交额: float = 0
        self.手续费: float = 0
        self.滑点: float = 0

        self.交易盈亏: float = 0
        self.持仓盈亏: float = 0
        self.总盈亏: float = 0
        self.净盈亏: float = 0

    def 添加成交(self, 成交: 类_成交数据) -> None:
        """"""
        self.成交列表.append(成交)

    def 计算盈亏(
        self,
        前收盘价: float,
        起始仓位: float,
        合约乘数: float,
        手续费: float,
        滑点: float
    ) -> None:
        """"""
        # 如果第一天没有提供前收盘价，使用值1避免除以零错误
        if 前收盘价:
            self.前收盘价 = 前收盘价
        else:
            self.前收盘价 = 1

        # 持仓盈亏是当天开始持有仓位的盈亏
        self.起始仓位 = 起始仓位
        self.结束仓位 = 起始仓位

        self.持仓盈亏 = self.起始仓位 * (self.收盘价 - self.前收盘价) * 合约乘数

        # 交易盈亏是当天新交易产生的盈亏
        self.成交笔数 = len(self.成交列表)
        print(f'长度：{len(self.成交列表)}')

        for 成交 in self.成交列表:
            if 成交.开平.value == '开':
                if 成交.方向.value == '空':
                    self.空单价格列表.append(成交.价格)
                    self.空单仓位.append(成交.数量)
                    self.空单持仓均价 = sum(self.空单价格列表) / len(self.空单价格列表)
                else:
                    self.多单价格列表.append(成交.价格)
                    self.多单仓位.append(成交.数量)
                    self.多单持仓均价 = sum(self.多单价格列表) / len(self.多单价格列表)
            else:
                if 成交.方向.value == '多' and self.空单持仓均价 != 0:
                    # 卖出开仓，买入平仓，所以成交方向是 多 ，但是是平空单
                    self.交易盈亏 += (self.空单持仓均价 - 成交.价格) * 成交.数量 * 合约乘数 - (成交.数量 * 手续费)
                    self.空单价格列表 = []
                    self.空单仓位 = []
                else:
                    if self.多单持仓均价 != 0:
                        # 买入开仓，卖出平仓，所以成交方向是 空 ，但是是多空单
                        self.交易盈亏 += (成交.价格 - self.多单持仓均价) * 成交.数量 * 合约乘数 - (成交.数量 * 手续费)
                        self.多单价格列表 = []
                        self.多单仓位 = []
                print(f'self.交易盈亏：{self.交易盈亏}')

            # -----------------------------------
            成交额: float = 成交.数量 * 合约乘数 * 成交.价格
            self.滑点 += 成交.数量 * 合约乘数 * 滑点

            self.成交额 += 成交额
            self.手续费 += 手续费 / 2

        空单持仓盈亏 = 0
        多单持仓盈亏 = 0
        if self.空单价格列表:
            空单持仓盈亏 = sum(self.空单仓位) * (self.收盘价 - self.空单持仓均价) * 合约乘数
            print(f'空单持仓盈亏：{空单持仓盈亏}')
        elif self.多单价格列表:
            多单持仓盈亏 = sum(self.多单仓位) * (self.收盘价 - self.多单持仓均价) * 合约乘数
            print(f'多单持仓盈亏：{多单持仓盈亏}')


        self.持仓盈亏 = 空单持仓盈亏 + 多单持仓盈亏

        # 净盈亏考虑手续费和滑点成本
        self.总盈亏 = self.交易盈亏 + self.持仓盈亏
        self.净盈亏 = self.总盈亏 - self.滑点


@lru_cache(maxsize=999)
def 加载K线数据(
    代码: str,
    交易所: 类_交易所,
    周期: 类_周期,
    开始时间: datetime,
    结束时间: datetime
) -> list[类_K线数据]:
    """"""
    数据库: 类_基础数据库 = 获取数据库()

    return 数据库.加载K线数据(代码, 交易所, 周期, 开始时间, 结束时间)       # type: ignore


@lru_cache(maxsize=999)
def 加载Tick数据(
    代码: str,
    交易所: 类_交易所,
    开始时间: datetime,
    结束时间: datetime
) -> list[类_行情数据]:
    """"""
    数据库: 类_基础数据库 = 获取数据库()

    return 数据库.加载Tick数据(代码, 交易所, 开始时间, 结束时间)       # type: ignore

def 获取目标值(结果: list) -> float:
    """
    获取用于排序优化结果的目标值
    """
    return cast(float, 结果[1])

def 单次回测(args: tuple) -> tuple[dict, dict]:
    """执行单次回测，返回 (参数, 指标)"""
    引擎参数, 策略类, 策略参数 = args

    引擎 = 类_回测引擎()
    引擎.设置参数(**引擎参数)
    引擎.添加策略(策略类, 策略参数)
    引擎.加载数据()
    引擎.运行回测()
    引擎.计算结果()
    指标 = 引擎.计算统计指标(是否打印结果=False)

    return 策略参数, 指标

def 参数优化(
    引擎参数: dict,
    策略类,
    优化设置: 类_优化设置,
    进程数: int | None = None
):
    if not 检查优化设置(优化设置):
        return []

    """使用多进程进行策略参数优化"""
    参数组合列表 = 优化设置.生成参数组合()
    任务列表 = [(引擎参数, 策略类, 策略参数) for 策略参数 in 参数组合列表]

    print("开始执行多进程优化")
    print(f"参数优化空间：{len(任务列表)}")

    # 记录开始时间
    开始时间: float = perf_counter()

    结果列表 = []
    with mp.Pool(processes=进程数 or mp.cpu_count()) as pool:
        for 策略参数, 指标 in tqdm(
            pool.imap(单次回测, 任务列表),
            total=len(任务列表),
            desc="优化进度"
        ):
            结果列表.append((策略参数, 指标))

        # 按优化目标值从大到小排序
        # 这里只在排序时提取优化目标
        排序结果 = sorted(
            结果列表,
            key=lambda x: x[1].get(优化设置.优化目标, float("-inf")),
            reverse=True
        )

        print(f"\n=== 参数优化结果 (按 {优化设置.优化目标} 从大到小排序) ===")
        for i, (参数, 指标) in enumerate(排序结果, 1):
            值 = 指标.get(优化设置.优化目标, "N/A")
            print(f"{i:03d}. {参数} -> {优化设置.优化目标}: {值}")

        # 计算耗时并输出
        结束时间: float = perf_counter()
        耗时: int = int(结束时间 - 开始时间)
        print(f"多进程参数优化完成，耗时{耗时}秒")

        return 排序结果

