# Lesson2：Backtrader来啦：数据篇
# link: https://mp.weixin.qq.com/s/NTct2_AYhz4Z8q5MYtBQcA
#%%


#%%
import backtrader as bt
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
# 海天味业
data3 = get_data_bytushare('603288.SH','20200101','20211015')

# %%

# 实例化策略
cerebro = bt.Cerebro()

st_date = datetime.datetime(2020,1,1)
ed_date = datetime.datetime(2021,10,15)

# 添加 600276.SH 的行情数据
datafeed1 = bt.feeds.PandasData(dataname=data1, fromdate=st_date, todate=ed_date)
cerebro.adddata(datafeed1, name='600276.SH')

# 添加 600519.SH 的行情数据
datafeed2 = bt.feeds.PandasData(dataname=data2, fromdate=st_date, todate=ed_date)
cerebro.adddata(datafeed2, name='600519.SH')

# 添加 603288.SH 的行情数据
datafeed3 = bt.feeds.PandasData(dataname=data3, fromdate=st_date, todate=ed_date)
cerebro.adddata(datafeed3, name='603288.SH')


#%%
# 第一章 DataFeed的数据结构

# 第1.1节：验证 data 的结构
class TestStrategy(bt.Strategy):
    def __init__(self):
        # 打印数据集和数据集对应的名称
        print("-------------self.datas-------------")
        print(self.datas)
        print("-------------self.data-------------")
        print(self.data._name, self.data) # 返回第一个导入的数据表格，缩写形式
        print("-------------self.data0-------------")
        print(self.data0._name, self.data0) # 返回第一个导入的数据表格，缩写形式
        print("-------------self.datas[0]-------------")
        print(self.datas[0]._name, self.datas[0]) # 返回第一个导入的数据表格，常规形式
        print("-------------self.datas[1]-------------")
        print(self.datas[1]._name, self.datas[1]) # 返回第二个导入的数据表格，常规形式
        print("-------------self.datas[-1]-------------")
        print(self.datas[-1]._name, self.datas[-1]) # 返回最后一个导入的数据表格
        print("-------------self.datas[-2]-------------")
        print(self.datas[-2]._name, self.datas[-2]) # 返回倒数第二个导入的数据表格

cerebro.addstrategy(TestStrategy)
result = cerebro.run()

#%%

# 第1.2节：验证 line 的结构
class TestStrategy(bt.Strategy):
    def __init__(self):
        print("--------- 打印 self 策略本身的 lines ----------")
        print(self.lines.getlinealiases())
        print("--------- 打印 self.datas 第一个数据表格的 lines ----------")
        print(self.datas[0].lines.getlinealiases())
        # 计算第一个数据集的s收盘价的20日均线，返回一个 Data feed
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=20)
        print("--------- 打印 indicators 对象的 lines ----------")
        print(self.sma.lines.getlinealiases())
        print("---------- 直接打印 indicators 对象的所有 lines -------------")
        print(self.sma.lines)
        print("---------- 直接打印 indicators 对象的第一条 lines -------------")
        print(self.sma.lines[0])
        
    def next(self):
        print('验证索引位置为 6 的线是不是 datetime')
        # datetime 线中的时间点存的是数字形式的时间，可以通过 bt.num2date() 方法将其转为“xxxx-xx-xx xx:xx:xx”这种形式
        print(bt.num2date(self.datas[0].lines[6][0]))

        
cerebro.addstrategy(TestStrategy)
result = cerebro.run()
#%%

# 第3节：提取 line 上的数据点，使用 get(ago,size) 切片函数
class TestStrategy(bt.Strategy):
    def __init__(self):
        self.count = 0 # 用于计算 next 的循环次数
        # 打印数据集和数据集对应的名称
        print("------------- init 中的索引位置-------------")
        # 对 datetime 线进行索引时，xxx.date(X) 可以直接以“xxxx-xx-xx xx:xx:xx”的形式返回，X 就是索引位置，可以看做是传统 [X] 索引方式的改进版 
        print("0 索引：",'datetime',self.data1.lines.datetime.date(0), 'close',self.data1.lines.close[0])
        print("-1 索引：",'datetime',self.data1.lines.datetime.date(-1),'close', self.data1.lines.close[-1])
        print("-2 索引",'datetime', self.data1.lines.datetime.date(-2),'close', self.data1.lines.close[-2])
        print("1 索引：",'datetime',self.data1.lines.datetime.date(1),'close', self.data1.lines.close[1])
        print("2 索引",'datetime', self.data1.lines.datetime.date(2),'close', self.data1.lines.close[2])
        # 通过 get() 切片时，如果是从 ago=0 开始取，不会返回数据，从其他索引位置开始取，能返回数据
        print("从 0 开始往前取3天的收盘价：", self.data1.lines.close.get(ago=0, size=3))
        print("从-1开始往前取3天的收盘价：", self.data1.lines.close.get(ago=-1, size=3))
        print("从-2开始往前取3天的收盘价：", self.data1.lines.close.get(ago=-2, size=3))
        print("line的总长度：", self.data1.buflen())
        
    def next(self):
        print(f"------------- next 的第{self.count+1}次循环 --------------")
        print("当前时点（今日）：",'datetime',self.data1.lines.datetime.date(0),'close', self.data1.lines.close[0])
        print("往前推1天（昨日）：",'datetime',self.data1.lines.datetime.date(-1),'close', self.data1.lines.close[-1])
        print("往前推2天（前日）", 'datetime',self.data1.lines.datetime.date(-2),'close', self.data1.lines.close[-2])
        print("前日、昨日、今日的收盘价：", self.data1.lines.close.get(ago=0, size=3))
        print("往后推1天（明日）：",'datetime',self.data1.lines.datetime.date(1),'close', self.data1.lines.close[1])
        print("往后推2天（明后日）", 'datetime',self.data1.lines.datetime.date(2),'close', self.data1.lines.close[2])
        # 在 next() 中调用 len(self.data0)，返回的是当前已处理（已回测）的数据长度，会随着回测的推进动态增长
        print("已处理的数据点：", len(self.data1))
        # buflen() 返回整条线的总长度，固定不变；
        print("line的总长度：", self.data0.buflen())
        self.count += 1

cerebro.addstrategy(TestStrategy)
result = cerebro.run()

#%%

# 第二章 DataFeeds 数据模块

# 第2.1节 默认的导入方式
'''
Backtrader 中的数据表格默认情况下包含 7 条 line，这 7 条 line 的位置也是固定的，
依次为 ('close', 'low', 'high', 'open', 'volume', 'openinterest', 'datetime') ，
那导入的数据表格必须包含这 7 个指标吗？指标的排列顺序也必须一致吗？当然不是！
其实你只要告诉 GenericCSVData、PandasData 、PandasDirectData 这 7 个指标在数据源中位于第几列，
如果没有这个指标，那就将位置设置为 -1 （如果是dataframe，None 表示指标不存在，-1 表示按位置或名称自动匹配指标），
所以你要做的是让 Backtrader 知道指标在数据源的哪个位置上。
'''

# 读取和导入 CSV 文件
data = bt.feeds.GenericCSVData(dataname='filename.csv')
cerebro.adddata(data, name='XXX')

# 读取和导入 dataframe 数据框 - 方式1
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data, name='XXX')

# 读取和导入 dataframe 数据框 - 方式2
data = bt.feeds.PandasDirectData(dataname=df)
cerebro.adddata(data, name='XXX')

# 以 GenericCSVData 为例进行参数说明（其他导入函数参数类似）
bt.feeds.GenericCSVData(dataname='daily_price.csv', # 数据源，CSV文件名 或 Dataframe对象
                        fromdate=st_date, # 读取的起始时间
                        todate=ed_date, # 读取的结束时间
                        nullvalue=0.0, # 缺失值填充
                        dtformat=('%Y-%m-%d'), # 日期解析的格式
                        # 下面是数据表格默认包含的 7 个指标，取值对应指标在 daily_price.csv 中的列索引位置
                        datetime=0, # 告诉 GenericCSVData， datetime 在 daily_price.csv 文件的第1列
                        high=3,
                        low=4,
                        open=2,
                        close=5,
                        volume=6,
                        openinterest=-1) # 如果取值为 -1 , 告诉 GenericCSVData 该指标不存在

#%%
# 第2.2节 自定义读取函数
'''
如果你觉得每次都要设置这么多参数来告知指标位置很麻烦，那你也可以重新自定义数据读取函数，
自定义的方式就是继承数据加载类 GenericCSVData、PandasData 再构建一个新的类，然后在新的类里统一设置参数。

自定义的函数，不会修改 Backtrader 底层的数据表格内 lines 的排列规则。
自定义的数据读取函数只是规定了一个新的数据读取规则，调用这个函数，就按函数里设置的规则来读数据，而不用每次都设置一堆参数。
'''
class My_CSVData(bt.feeds.GenericCSVData):
    params = (
                ('fromdate', datetime.datetime(2019,1,2)),
                ('todate', datetime.datetime(2021,1,28)),
                ('nullvalue', 0.0),
                ('dtformat', ('%Y-%m-%d')),
                ('datetime', 0),
                ('time', -1),
                ('high', 3),
                ('low', 4),
                ('open', 2),
                ('close', 5),
                ('volume', 6),
                ('openinterest', -1)
            )

cerebro = bt.Cerebro()
data = My_CSVData(dataname='daily_price.csv')
cerebro.adddata(data, name='600466.SH')
result = cerebro.run()

#%%
# 第2.3节 新增指标
'''
在回测时，除了常规的高开低收成交量这些行情数据外，还会用到别的指标，
比如选股回测时会用到很多选股因子（PE、PB 、PCF、......），那这些数据又该如何添加进 Backtrader 的数据表格呢？
往 Backtrader 的数据表格里添加指标，就是给数据表格新增列，也就是给数据表格新增 line：
以导入 DataFrame 为例，在继承原始的数据读取类 bt.feeds.PandasData 的基础上，
设置 lines 属性和 params 属性，新的 line 会按其在 lines 属性中的顺序依次添加进数据表格中，
具体对照下面例子的输出部分：
'''

class PandasData_more(bt.feeds.PandasData):
    lines = ('pe', 'pb', ) # 要添加的线
    # 设置 line 在数据源上的列位置
    params=(
             ('pe', -1),
             ('pb', -1),
            )
    # -1表示自动按列明匹配数据，也可以设置为线在数据源中列的位置索引 (('pe',6),('pb',7),)

class TestStrategy(bt.Strategy):
    def __init__(self):
        print("--------- 打印 self.datas 第一个数据表格的 lines ----------")
        print(self.data0.lines.getlinealiases())
        print("pe line:", self.data0.lines.pe)
        print("pb line:", self.data0.lines.pb)

data1['pe'] = 2 # 给原先的data1新增pe指标（简单的取值为2）
data1['pb'] = 3 # 给原先的data1新增pb指标（简单的取值为3）

# 导入的数据 data1 中
cerebro = bt.Cerebro()
st_date = datetime.datetime(2020,1,1)
ed_date = datetime.datetime(2021,10,15)

# 这里使用上述定义的新类PandasData_more（继承了bt.feeds.PandasData）
datafeed1 = PandasData_more(dataname=data1, fromdate=st_date, todate=ed_date)
cerebro.adddata(datafeed1, name='600276.SH')
cerebro.addstrategy(TestStrategy)
result = cerebro.run()
