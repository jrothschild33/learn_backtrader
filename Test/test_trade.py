import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import backtrader as bt
import tushare as ts
token = 'd9645bfd8516b93f1312d8ba696c83b606a78d966e71ec5c1e79bef4'
ts.set_token(token) 
pro = ts.pro_api(token)


# 使用Tushare获取数据，要严格保持OHLC的格式
df = ts.pro_bar(ts_code='600276.SH', adj='qfq',start_date='20200101', end_date='20211015')
df = df[['trade_date', 'open', 'high', 'low', 'close','vol']]
df.columns = ['trade_date', 'open', 'high', 'low', 'close','volume']
df.trade_date = pd.to_datetime(df.trade_date)
# 索引必须是日期
df.index = df.trade_date
# 日期必须要升序
df.sort_index(inplace=True)

# Create a Stratey
class TestStrategy(bt.Strategy):
    # 设定参数，便于修改
    params = (
        ('maperiod', 30),
    )

    def log(self, txt, dt=None):
        ''' 
        日志函数：打印结果
        datas[0]：传入的数据，包含日期、OHLC等数据
        datas[0].datetime.date(0)：调用传入数据中的日期列
        '''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # dataclose变量：跟踪当前收盘价
        self.dataclose = self.datas[0].close

        # order变量：跟踪订单状态
        self.order = None
        # buyprice变量：买入价格
        self.buyprice = None
        # buycomm变量：买入时佣金费用
        self.buycomm = None

        # 指标：简单移动平均 MovingAverageSimple【15天】
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0],period=self.params.maperiod)
        
        # 添加画图专用指标
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        '''订单状态通知(order.status)：提示成交状态'''
        if order.status in [order.Submitted, order.Accepted]:
            # 如果订单只是提交状态，那么啥也不提示
            return

        # 检查订单是否执行完毕
        # 注意：如果剩余现金不足，则会被拒绝！
        if order.status in [order.Completed]:
            if order.isbuy():
                # 买入信号记录：买入价、买入费用、买入佣金费用
                self.log(
                        'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():
                # 卖出信号记录：卖出价、卖出费用、卖出佣金费用
                self.log(
                        'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                        (order.executed.price,
                         order.executed.value,
                         order.executed.comm))
            
            # 记录订单执行的价格柱的编号（即长度）
            self.bar_executed = len(self)

        # 如果订单被取消/保证金不足/被拒绝
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # 如果没有查询到订单，则订单为None
        self.order = None

    def notify_trade(self, trade):
        '''交易状态通知：查看交易毛/净利润'''
        if not trade.isclosed:
            return
        # 交易毛利润：trade.pnl、交易净利润：trade.pnlcomm（扣除佣金）
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))


    # 交易策略主函数
    def next(self):
        # 记录收盘价
        self.log('Close, %.2f' % self.dataclose[0])

        # 检查一下是否有订单被挂起，如果有的话就先不下单
        if self.order:
            return
        
        # 检查一下目前是否持有头寸，如果没有就建仓
        if not self.position:
            # 如果现价>【15日】均线
            if self.dataclose[0] > self.sma[0]:
                # 买买买！先记录一下买入价格（收盘价）
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # 更新订单状态：buy()：开仓买入，买入价是下一个数据，即【开盘价】
                self.order = self.buy()
        else:
             # 如果已经建仓，并持有头寸，则执行卖出指令
             # 如果现价<【15日】均线
            if self.dataclose[0] < self.sma[0]:
                # 卖!卖!卖!
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # 更新订单状态：sell()：平仓卖出，卖出价是下一个数据，即【开盘价】
                self.order = self.sell()

# 创建实例
cerebro = bt.Cerebro()
 # 添加策略
cerebro.addstrategy(TestStrategy)
# 添加数据源
data = bt.feeds.PandasData(dataname=df)
# 输入数据源
cerebro.adddata(data)
# 设置初始现金：10万
cerebro.broker.setcash(100000.0)
# 设定每次买入的股票数量：10股
cerebro.addsizer(bt.sizers.FixedSize, stake=1000)
# 设置佣金费率：双边0.1%
cerebro.broker.setcommission(commission=0.001)
# 显示：初始资产
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
# 运行策略
cerebro.run()
# 显示：最终资产
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
# 画出图像
cerebro.plot()