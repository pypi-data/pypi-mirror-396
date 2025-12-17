from xmpy_ctastrategy import (
    类_CTA策略模板,
    类_停止单,
    类_行情数据,
    类_K线数据,
    类_成交数据,
    类_订单数据,
    类_K线生成器,
    类_数组管理器
)

class 示例策略_基础教程(类_CTA策略模板):
    作者 = "bhzyxyqy"

    # 策略参数
    初始手数 = 0

    # 策略变量
    计数 = 0

    # 写入参数和变量列表的会分别写入到文件 cta_参数设置.json，cta_变量数据.json中，没有写入列表的则不会
    参数列表 = ["初始手数"]
    变量列表 = ["计数"]

    def 初始化回调(self):
        self.记录日志("策略初始化回调")

    def 启动回调(self):
        self.记录日志("策略启动")

    def 停止回调(self):
        self.记录日志("策略停止")

    def 行情回调(self, tick: 类_行情数据):
        self.计数 += 1
        self.记录日志(f'tick当前计数：{self.计数}')
        if self.计数 == 30:
            self.买入开仓(tick.卖一价,self.初始手数)
        elif self.计数 == 40:
            self.卖出平仓(tick.买一价, self.初始手数)

        elif self.计数 == 50:
            self.卖出开仓(tick.买一价, self.初始手数)
        elif self.计数 == 60:
            self.买入开仓(tick.卖一价,self.初始手数)

    def K线回调(self, K线: 类_K线数据):
        self.记录日志(f'K线回调：{K线}')

    def 委托回调(self, 委托: 类_订单数据):
        self.记录日志(f'委托回报：{委托}')

    def 成交回调(self, 成交: 类_成交数据):
        self.记录日志(f'成交回报：{成交}')

    def 停止单回调(self, 停止单: 类_停止单):
        self.记录日志(f'停止单回调：{停止单}')