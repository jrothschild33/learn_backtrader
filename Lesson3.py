# Lesson3：Backtrader来啦：指标篇
# link: https://mp.weixin.qq.com/s/rFaU96l4mYzC0Kaua9jRJA

# 官方文档：https://www.backtrader.com/docu/indautoref/
'''
在编写策略时，除了常规的高开低收成交量等行情数据外，还会用到各式各样的指标（变量），
比如宏观经济指标、基本面分析指标、技术分析指标、另类数据等等。Backtrader 大致有 2 种获取指标的方式：

1、直接通过 DataFeeds 模块导入已经计算好的指标，比如《数据篇》中的导入新增指标 PE、PB；
2、在编写策略时调用 Indicators 指标模块临时计算指标，比如 5 日均线、布林带等 。
'''

#%%
import backtrader as bt
import backtrader.indicators as btind # 导入策略分析模块
import pandas as pd
import datetime

import tushare as ts
import json
with open(r'Data/tushare_token.json','r') as load_json:
    token_json = json.load(load_json)
token = token_json['token']
ts.set_token(token) 
pro = ts.pro_api(token)
#%%
# 使用Tushare获取数据，要严格保持OHLC的格式

def get_data_bytushare(code,start_date,end_date):
    df = ts.pro_bar(ts_code=code, adj='qfq',start_date=start_date, end_date=end_date)
    df = df[['trade_date', 'open', 'high', 'low', 'close','vol']]
    df.columns = ['trade_date', 'open', 'high', 'low', 'close','volume']
    df.trade_date = pd.to_datetime(df.trade_date)
    df.index = df.trade_date
    df.sort_index(inplace=True)
    df.fillna(0.0,inplace=True)
    return df

# 恒瑞医药
data1 = get_data_bytushare('600276.SH','20200101','20211015')
# 贵州茅台
data2 = get_data_bytushare('600519.SH','20200101','20211015')
#%%

# 第1节 建议在 __init__() 中提前计算指标
'''
Strategy 中的 __init__() 函数在回测过程中只会在最开始的时候调用一次，而 next() 会每个交易日依次循环调用多次，
所以为了提高回测效率，建议先在 __init__() 中一次性计算好指标（甚至是交易信号），然后在 next() 中调用已经算好的指标，
这样能有效避免指标的重复计算，提高回测运行速度。

建议遵循“__init__() 负责指标计算，next() 负责指标调用”的原则。
'''

class MyStrategy(bt.Strategy):
  # 先在 __init__ 中提前算好指标
    def __init__(self):
        self.sma1 = btind.SimpleMovingAverage(self.data)
        self.ema1 = btind.ExponentialMovingAverage()
        self.close_over_sma = self.data.close > self.sma1
        self.close_over_ema = self.data.close > self.ema1
        self.sma_ema_diff = self.sma1 - self.ema1
        # 生成交易信号
        self.buy_sig = bt.And(self.close_over_sma, self.close_over_ema, self.sma_ema_diff > 0)

    # 在 next 中直接调用计算好的指标
    def next(self):
        if self.buy_sig:
            self.buy()

#%%
# 第2节 计算指标时的各种简写形式
# 默认：对 close 进行计算
'''
调用指标时会涉及 line 的索引和切片操作，为了使操作更加简便，在 next() 中调用当前时刻指标值时，
可以省略索引 [0] ：即在 next() 中，
self.sma5[0] ↔ self.sma5、self.data.close[0] ↔ self.data.close 等都是等价的，
省略了 [0] 的简写形式 self.sma5 、 self.data.close 等都默认指向当前值，自动索引当前值。
'''

class TestStrategy(bt.Strategy):
    def __init__(self):
        # 指标函数也支持简写 SimpleMovingAverage → SMA
        # 最简方式：直接省略指向的数据集
        self.sma1 = btind.SimpleMovingAverage(period=5)
        # 只指定第一个数据表格
        self.sma2 = btind.SMA(self.data, period=5)
        # 指定第一个数据表格的 close 线
        self.sma3 = btind.SMA(self.data.close, period=5)
        # 完整写法
        self.sma4 = btind.SMA(self.datas[0].lines[0], period=5)
        
        
    def next(self):
        # 提取当前时间点
        print('datetime', self.datas[0].datetime.date(0))
        # 打印当日、昨日、前日的均线
        print('sma1',self.sma1.get(ago=0, size=3))
        print('sma2',self.sma2.get(ago=0, size=3))
        print('sma3',self.sma3.get(ago=0, size=3))
        print('sma4',self.sma4.get(ago=0, size=3))
        
cerebro = bt.Cerebro()
st_date = datetime.datetime(2020,1,1)
end_date = datetime.datetime(2021,10,12)
datafeed1 = bt.feeds.PandasData(dataname=data1, fromdate=st_date, todate=end_date)
cerebro.adddata(datafeed1, name='600276.SH')
datafeed2 = bt.feeds.PandasData(dataname=data2, fromdate=st_date, todate=end_date)
cerebro.adddata(datafeed2, name='600519.SH')

cerebro.addstrategy(TestStrategy)
result = cerebro.run()

#%%
# 第3节 好用的运算函数
'''
在计算指标或编写策略逻辑时，离不开算术运算、关系运算、逻辑运算、条件运算......，
为了更好的适用于Backtrader 框架的语法规则，Backtrader 的开发者还对一些常用的运算符做了优化和改进，
使用起来更简便高效：And、Or、If、All、Any、Max、Min、Sum、Cmp...

在next()中返回的结果依然是line，可以通过[num]调用各个时间节点的数值
'''

class TestStrategy(bt.Strategy):
    
    def __init__(self):
        self.sma5 = btind.SimpleMovingAverage(period=5) # 5日均线
        self.sma10 = btind.SimpleMovingAverage(period=10) # 10日均线
        # bt.And 中所有条件都满足时返回 1；有一个条件不满足就返回 0
        self.And = bt.And(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Or 中有一个条件满足时就返回 1；所有条件都不满足时返回 0
        self.Or = bt.Or(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.If(a, b, c) 如果满足条件 a，就返回 b，否则返回 c
        self.If = bt.If(self.data>self.sma5,1000, 5000)
        # bt.All,同 bt.And
        self.All = bt.All(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Any，同 bt.Or
        self.Any = bt.Any(self.data>self.sma5, self.data>self.sma10, self.sma5>self.sma10)
        # bt.Max，返回同一时刻所有指标中的最大值
        self.Max = bt.Max(self.data, self.sma10, self.sma5)
        # bt.Min，返回同一时刻所有指标中的最小值
        self.Min = bt.Min(self.data, self.sma10, self.sma5)
        # bt.Sum，对同一时刻所有指标进行求和
        self.Sum = bt.Sum(self.data, self.sma10, self.sma5)
        # bt.Cmp(a,b), 如果 a>b ，返回 1；否则返回 -1
        self.Cmp = bt.Cmp(self.data, self.sma5)
        
    def next(self):
        print('---------- datetime',self.data.datetime.date(0), '------------------')
        print('close:', self.data[0], 'ma5:', self.sma5[0], 'ma10:', self.sma10[0])
        print('close>ma5',self.data>self.sma5, 'close>ma10',self.data>self.sma10, 'ma5>ma10', self.sma5>self.sma10)
        print('self.And', self.And[0], self.data>self.sma5 and self.data>self.sma10 and self.sma5>self.sma10)
        print('self.Or', self.Or[0], self.data>self.sma5 or self.data>self.sma10 or self.sma5>self.sma10)
        print('self.If', self.If[0], 1000 if self.data>self.sma5 else 5000)
        print('self.All',self.All[0], self.data>self.sma5 and self.data>self.sma10 and self.sma5>self.sma10)
        print('self.Any', self.Any[0], self.data>self.sma5 or self.data>self.sma10 or self.sma5>self.sma10)
        print('self.Max',self.Max[0], max([self.data[0], self.sma10[0], self.sma5[0]]))
        print('self.Min', self.Min[0], min([self.data[0], self.sma10[0], self.sma5[0]]))
        print('self.Sum', self.Sum[0], sum([self.data[0], self.sma10[0], self.sma5[0]]))
        print('self.Cmp', self.Cmp[0], 1 if self.data>self.sma5 else -1)
        
cerebro = bt.Cerebro()
st_date = datetime.datetime(2020,1,1)
ed_date = datetime.datetime(2021,10,15)
datafeed1 = bt.feeds.PandasData(dataname=data1, fromdate=st_date, todate=ed_date)
cerebro.adddata(datafeed1, name='600466.SH')
cerebro.addstrategy(TestStrategy)
result = cerebro.run()

#%%
# 第4节 如何对齐不同周期的指标
'''
通常情况下，操作的都是相同周期的数据，比如日度行情数据计算返回各类日度指标、周度行情数据计算返回各类周度指标、......，
行情数据和指标的周期是一致的，时间也是对齐的。但有时候也会遇到操作不同周期数据的情况，比如拿日度行情与月度指标作比较，
日度行情每天都有数据，而月度指标每个月只有一个，2 条数据在时间上是没有对齐的。

可以使用“ ( ) ”语法操作来对齐不同周期的数据，对齐的方向是“大周期向小周期对齐”，
可以选择指标对象中的某条 line 进行对齐，也可以对整个指标对象进行对齐。

“ ( ) ”语法类似于线的切片操作 get (ago=-1, size=1)，然后在更细的时间点上始终取当前最新的指标值。
比如对于月度指标，向日度对齐时，月中的那些时间点的数据取得是当前最新的数据（即：月初的指标值），
直到下个月月初新的指标值计算出来为止

在使用该语法时，要将 cerebro.run() 中的 runonce 设置为 False，才能实现对齐操作。
'''

# 注：在 Backtrader 中，当前月计算的月度指标是存给下个月第一个交易日的，
# 比如月度数据 2019-02-01 的指标值，就是用 1 月份数据计算出来的指标值；
# 2019-03-01 的指标值对应的是 2 月份数据计算出来的指标值等。

class TestStrategy(bt.Strategy):
    
    def __init__(self):
        # self.data0 是日度行情、self.data1 是月度行情
        # 计算返回的 self.month 指标也是月度的
        self.month = btind.xxx(self.data1) 
        # 选择指标对象中的第一条 line 进行对齐
        self.sellsignal = self.data0.close < self.month.lines[0]()
        # 对齐整个指标对象
        self.month_ = self.month()
        self.signal = self.data0.close < self.month_.lines[0]

cerebro.run(runonce=False)

#%%
# 第5节 在 Backtrader 中调用 TA-Lib 库
'''
为了满足大家的使用习惯，Backtrader 还接入了 TA-Lib 技术指标库，
具体信息可以查阅官方 document ：https://www.backtrader.com/docu/talibindautoref/
文档中同样对各个函数的输入、输出，以及在 Backtrader 中特有的绘图参数、返回的 lines 属性等信息都做了介绍和说明。
TA-Lib 指标函数的调用形式为 bt.talib.xxx
'''

class TALibStrategy(bt.Strategy):
    def __init__(self):
        # 计算 5 日均线
        bt.talib.SMA(self.data.close, timeperiod=5)
        bt.indicators.SMA(self.data, period=5)
        # 计算布林带
        bt.talib.BBANDS(self.data, timeperiod=25)
        bt.indicators.BollingerBands(self.data, period=25)

#%%
# 第6节 自定义新指标
'''
在 Backtrader 中，如果涉及到自定义操作，一般都是通过继承原始的父类，然后在新的子类里自定义属性，
比如之前介绍的自定义数据读取函数 class My_CSVData (bt.feeds.GenericCSVData)，就是继承了原始GenericCSVData 类，
自定义新指标也类似，需要继承原始的 bt.Indicator 类，然后在新的子类里构建指标。
'''
class MyInd(bt.Indicator):
    # 定义指标函数返回的 lines 名称，方便后面通过名称调用具体的指标，如 self.lines.xxx、self.l.xxx、self.xxx
    lines = (xxx,xxx, ) # 最后一个 “,” 别省略
    # 定义参数 params，方便在子类里全局调用，也方便在使用指标函数时修改参数取值；
    params = ((xxx, n),) # 最后一个 “,” 别省略
    
    # __init__() 方法：同策略 Strategy 里的 __init__() 类似，对整条 line 进行运算，运算结果也以整条 line 的形式返回；
    def __init__(self):
        '''可选'''
        pass
    
    # next() 方法：同策略 Strategy 里的 next() 类似，每个 bar 都会运行一次，在 next() 中是对数据点进行运算；
    def next(self):
        '''可选'''
        pass
    
    # once() 方法：这个方法只运行一次，但是需要从头到尾循环计算指标；
    def once(self):
        '''可选'''
        pass 
    
    # 指标绘图相关属性的设置：例如：plotinfo = dict() 通过字典形式修改绘图参数；plotlines = dict() 设置曲线样式等...
    plotinfo = dict(...)
    plotlines = dict(...)

#%%
# 第6.1节 自定义新指标：举例

'重要提示：自定义指标时，建议首选 __init__()，因为 __init__() 最智能，能自动实现 next() 和 once() 的功能，计算指标一气呵成'

class DummyInd(bt.Indicator):
    # 将计算的指标命名为 'dummyline'，后面调用这根 line 的方式有：
    # self.lines.dummyline 、 self.l.dummyline 、 self.dummyline
    lines = ('dummyline',)
    # 定义参数，后面调用这个参数的方式有：
    # self.params.xxx 、 self.p.xxx
    params = (('value', 5),)
    
    def __init__(self):
        # __init__() 中是对 line 进行运算，最终也以 line 的形式返回，所以运算结果直接赋值给了 self.l.dummyline；
        self.l.dummyline = bt.Max(0.0, self.p.value)
    
    def next(self):
        # next() 中是对当前时刻的数据点进行运算（用了常规的 max() 函数），返回的运算结果也只是当前时刻的值，所以是将结果赋值给 dummyline 的当前时刻：self.l.dummyline[0]， 然后依次在每个 bar 都运算一次；
        self.l.dummyline[0] = max(0.0, self.p.value)
   
    def once(self, start, end):
        # once() 也只运行一次，是更为纯粹的 python 运算，少了 Backtrader 味道，不是直接对指标 line 进行操作，而只是单纯的 python 运算和赋值；
        dummy_array = self.l.dummyline.array
        for i in xrange(start, end):
            dummy_array[i] = max(0.0, self.p.value)
#%%
# 第6.2节 自定义新指标：以 MACD 为例

class My_MACD(bt.Indicator):
    lines = ('macd', 'signal', 'histo')
    params = (('period_me1',12),
              ('period_me2', 26),
              ('period_signal', 9),)

    def __init__(self):
        me1 = btind.EMA(self.data, period=self.p.period_me1)
        me2 = btind.EMA(self.data, period=self.p.period_me2)
        self.l.macd = me1 - me2
        self.l.signal = btind.EMA(self.l.macd, period=self.p.period_signal)
        self.l.histo = self.l.macd - self.l.signal