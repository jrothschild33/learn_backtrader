from __future__ import (absolute_import, division, print_function,unicode_literals)

import backtrader as bt
import numpy as np
import pandas as pd
# 画图
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [10, 5]
plt.rcParams['figure.dpi']=100
plt.rcParams['font.sans-serif'] = ['Times New Roman']
plt.rcParams["font.size"] = "10"

import tushare as ts
token = 'd9645bfd8516b93f1312d8ba696c83b606a78d966e71ec5c1e79bef4'
ts.set_token(token) 
pro = ts.pro_api(token)

# 使用Tushare获取数据，要严格保持OHLC的格式
df = ts.pro_bar(ts_code='600276.SH', adj='qfq',start_date='20160101', end_date='20210906')
df = df[['trade_date', 'open', 'high', 'low', 'close','vol']]
df.columns = ['trade_date', 'open', 'high', 'low', 'close','volume']
df.trade_date = pd.to_datetime(df.trade_date)
# 索引必须是日期
df.index = df.trade_date
# 日期必须要升序
df.sort_index(inplace=True)
df.fillna(0.0,inplace=True)


class St(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data)

cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)
cerebro.addstrategy(St)
cerebro.run()
cerebro.plot()