# Lesson4：Backtrader来啦：交易篇（上）
# link: https://mp.weixin.qq.com/s/30ShvEKmoyP07QBxHXnmUQ

'''
Step1：设置交易条件：初始资金、交易税费、滑点、成交量限制等；
Step2：在 Strategy 策略逻辑中下达交易指令 buy、sell、close，或取消交易 cancel；
Step3：Order 模块会解读交易订单，解读的信息将交由经纪商 Broker 模块处理；
Step4：经纪商 Broker 会根据订单信息检查订单并确定是否接收订单；
Step5：经纪商 Broker 接收订单后，会按订单要求撮合成交 trade，并进行成交结算；
Step6：Order 模块返回经纪商 Broker 中的订单执行结果。 
'''
# =============================================================================
#%%
# 第1章 Broker 中的交易条件
'''
回测过程中涉及的交易条件设置，最常见的有初始资金、交易税费、滑点、期货保证金比率等，
有时还会对成交量做限制、对涨跌幅做限制、对订单生成和执行时机做限制，
上述大部分交易条件都可以通过 Broker 来管理，主要有 2 中操作方式：

方式1：通过设置 backtrader.brokers.BackBroker() 类中的参数，生成新的 broker 实例，再将新的实例赋值给 cerebro.broker ;
方式2：通过调用 broker 中的 ”set_xxx“ 方法来修改条件，还可通过 ”get_xxx“ 方法查看当前设置的条件取值。
'''

# 第1.1节 资金管理
'''
Broker 默认的初始资金 cash 是 10000，可通过 “cash” 参数、set_cash() 方法修改初始资金，
此外还提供了add_cash() 方法增加或减少资金。Broker 会检查提交的订单现金需求与当前现金是否匹配，
cash 也会随着每次交易进行迭代更新用以匹配当前头寸。
'''
# 初始化时
cerebro.broker.set_cash(100000000.0) # 设置初始资金
cerebro.broker.get_cash() # 获取当前可用资金

# 简写形式
cerebro.broker.setcash(100000000.0) # 设置初始资金
cerebro.broker.getcash() # 获取当前可用资金

# 在 Strategy 中添加资金或获取当前资金
self.broker.add_cash(10000) # 正数表示增加资金
self.broker.add_cash(-10000) # 负数表示减少资金
self.broker.getcash() # 获取当前可用资金

#%%
# 第1.2节 持仓查询
'''
Broker 在每次交易后更新 cash 外，还会同时更新当前总资产 value 和当前持仓 position，通常在 Strategy 中进行持仓查询操作;

当前总资产 = 当前可用资金 + 当前持仓总市值，而当前持仓总市值为当前持仓中所有标的各自持仓市值之和，
如果只有一个标的，就有:当前总资产 999943.18 = 当前可用资金 996735.39 + 当前持仓数量 100.00 × 当前 close 32.0779；

在计算当前可用资金时，除了考虑扣除购买标的时的费用外，还需要考虑扣除交易费用 。
'''

class TestStrategy(bt.Strategy):
    def next(self):
        print('当前可用资金', self.broker.getcash())
        print('当前总资产', self.broker.getvalue())
        print('当前持仓量', self.broker.getposition(self.data).size)
        print('当前持仓成本', self.broker.getposition(self.data).price)
        # 也可以直接获取持仓
        print('当前持仓量', self.getposition(self.data).size)
        print('当前持仓成本', self.getposition(self.data).price)
        # 注：getposition() 需要指定具体的标的数据集
        
# =============================================================================
#%%
# 第2章 滑点管理
'''
在实际交易中，由于市场波动、网络延迟等原因，交易指令中指定的交易价格与实际成交价格会存在较大差别，出现滑点。
为了让回测结果更真实，在交易前可以通过 brokers 设置滑点，滑点的类型有 2 种：【百分比滑点】和【固定滑点】。
不论哪种设置方式，都是起到相同的作用：买入时，在指定价格的基础上提高实际买入价格；
卖出时，在指定价格的基础上，降低实际卖出价格；买的 “更贵”，卖的 “更便宜” 。

注：在 Backtrader 中，如果同时设置了百分比滑点和固定滑点，前者的优先级高于后者，最终按百分比滑点的设置处理。
'''

# 第2.1节 百分比滑点
'''
假设设置了 n% 的滑点，如果指定的买入价为 x，那实际成交时的买入价会提高至 x * (1+ n%) ；
同理，若指定的卖出价为 x，那实际成交时的卖出价会降低至 x * (1- n%)，下面时将滑点设置为 0.01% 的例子：
'''
# 方式1：通过 BackBroker 类中的 slip_perc 参数设置百分比滑点
cerebro.broker = bt.brokers.BackBroker(slip_perc=0.0001)

# 方式2：通过调用 brokers 的 set_slippage_perc 方法设置百分比滑点
cerebro.broker.set_slippage_perc(perc=0.0001)

#%%
# 第2.2节 固定滑点
'''
假设设置了大小为 n 的固定滑点，如果指定的买入价为 x，那实际成交时的买入价会提高至 x + n ；
同理，若指定的卖出价为 x，那实际成交时的卖出价会降低至 x - n，下面时将滑点固定为 0.001 的例子：
'''
# 方式1：通过 BackBroker 类中的 slip_fixed 参数设置固定滑点
cerebro.broker = bt.brokers.BackBroker(slip_fixed=0.001)

# 方式2：通过调用 brokers 的 set_slippage_fixed 方法设置固定滑点
cerebro.broker.set_slippage_fixed(fixed=0.001)

#%%
# 第2.3节 有关滑点的其他设置

'''
除了用于设置滑点的 slip_perc 和 slip_fixed 参数外，broker 还提供了其他参数用于处理价格出现滑点后的极端情况：

slip_open：是否对开盘价做滑点处理;
           该参数在 BackBroker() 类中默认为 False，
           在 set_slippage_perc 和set_slippage_fixed 方法中默认为 True；

slip_match：是否将滑点处理后的新成交价与成交当天的价格区间 low ~ high 做匹配;
            如果为 True，则根据新成交价重新匹配调整价格区间，确保订单能被执行，默认取值为 True；
            如果为 False，则不会与价格区间做匹配，订单不会执行，但会在下一日执行一个空订单；

slip_out：如果新成交价高于最高价或低于最高价，是否以超出的价格成交;
          如果为 True，则允许以超出的价格成交；(仅在slip_match=True时才有用，可以超出最高价/最低价执行；否则只能执行空订单)
          如果为 False，实际成交价将被限制在价格区间内  low ~ high，默认取值为 False；

slip_limit：是否对限价单执行滑点;
            如果为 True，即使 slip_match 为False，也会对价格做匹配，确保订单被执行，默认取值为 True；
            如果为 False，则不做价格匹配；
'''
# 方法1：
cerebro.broker = bt.brokers.BackBroker(..., slip_perc=0, slip_fixed=0,  slip_open=False, slip_match=True, slip_out=False, slip_limit=True, ...)

# 方法2：
cerebro.broker.set_slippage_fixed(..., fixed=..., slip_open=False, slip_match=True, slip_out=False, slip_limit=True, ...)

# 下面是将滑点设置为固定 0.35 ，对上述参数去不同的值，标的 600466.SH 在 2019-01-17 的成交情况做对比：
# 情况1：
'''由于 slip_open=False ，不会对开盘价做滑点处理，所以仍然以原始开盘价 32.63307367 成交'''
set_slippage_fixed(fixed=0.35,
                   slip_open=False,
                   slip_match=True,
                   slip_out=False)

# 情况2：
'''
滑点调整的新成交价为 32.63307367+0.35 = 32.98307367，超出了当天最高价 32.94151482
由于允许做价格匹配 slip_match=True, 但不以超出价格区间的价格执行 slip_out=False
最终以最高价 32.9415 成交
'''
set_slippage_fixed(fixed=0.35,
                   slip_open=True,
                   slip_match=True,
                   slip_out=False)

# 情况3：
'''
滑点调整的新成交价为 32.63307367+0.35 = 32.98307367，超出了当天最高价 32.94151482
允许做价格匹配 slip_match=True, 而且运行以超出价格区间的新成交价执行 slip_out=True
最终以新成交价 32.98307367 成交
'''
set_slippage_fixed(fixed=0.35,
                   slip_open=True,
                   slip_match=True,
                   slip_out=True)

# 情况4：
'''
滑点调整的新成交价为 32.63307367+0.35 = 32.98307367，超出了当天最高价 32.94151482
由于不进行价格匹配 slip_match=False，新成交价超出价格区间无法成交
2019-01-17 这一天订单不会执行，但会在下一日 2019-01-18 执行一个空订单
再往后的 2019-07-02，也未执行订单，下一日 2019-07-03 执行空订单
即使 2019-07-03的 open 39.96627412+0.35 < high 42.0866713 满足成交条件，也不会补充成交
'''
set_slippage_fixed(fixed=0.35,
                   slip_open=True,
                   slip_match=False,
                   slip_out=True)
# =============================================================================

#%%
# 第3章 交易税费管理
'''
【交易费收取规则】----------------------------------

股票：目前 A 股的交易费用分为 2 部分：佣金和印花税，
      1.佣金：双边征收，不同证券公司收取的佣金各不相同，一般在 0.02%-0.03% 左右，单笔佣金不少于 5 元；
      2.印花税：只在卖出时收取，税率为 0.1%。

期货：期货交易费用包括交易所收取手续费和期货公司收取佣金 2 部分，
      1.交易所手续费较为固定；
      2.不同期货公司佣金不一致，而且不同期货品种的收取方式不相同，有的按照固定费用收取，有的按成交金额的固定百分比收取：
        合约现价*合约乘数*手续费费率
      3.除了交易费用外，期货交易时还需上交一定比例的保证金

【交易费设置方式】----------------------------------

根据交易品种的不同：
    1. 股票 Stock-like 模式
    2. 期货 Futures-like 模式

根据计算方式的不同：
    1. PERC 百分比费用模式
    2. FIXED 固定费用模式

【交易费参数】----------------------------------

1. commission：手续费 / 佣金；
2. mult：乘数；
3. margin：保证金 / 保证金比率 。
4. 双边征收：买入和卖出操作都要收取相同的交易费用
'''

# 第3.1节 通过 BackBroker() 设置

# BackBroker 中有一个 commission 参数，用来全局设置交易手续费。如果是股票交易，可以简单的通过该方式设置交易佣金，但该方式无法满足期货交易费用的各项设置。
cerebro.broker = bt.brokers.BackBroker(commission= 0.0002)  # 设置 0.0002 = 0.02% 的手续费

#%%

# 第3.2节 通过 setcommission() 设置
# 如果想要完整又方便的设置交易费用，可以调用 broker 的 setcommission() 方法，该方法基本上可以满足大部分的交易费用设置需求
'''
从上述各参数的含义和作用可知，margin 、commtype、stocklike 存在 2 种默认的配置规则：股票百分比费用、期货固定费用，具体如下：

1. 未设置 margin（即 margin 为 0 / None / False）:
    commtype 会指向 COMM_PERC 百分比费用 → 底层的 _stocklike 属性会设置为 True → 对应的是“股票百分比费用”。
    所以如果想为股票设置交易费用，就令 margin = 0 / None / False，或者令 stocklike=True；

2. 为 margin 设置了取值 →  commtype 会指向 COMM_FIXED 固定费用 → 底层的 _stocklike 属性会设置为 False → 对应的是“期货固定费用”，因为只有期货才会涉及保证金。
   所以如果想为期货设置交易费用，就需要设置 margin，此外还需令 stocklike=True，margin 参数才会起作用 。
'''

cerebro.broker.setcommission(
                            # 交易手续费，根据margin取值情况区分是百分比手续费还是固定手续费
                            commission=0.0,
                            # 期货保证金，决定着交易费用的类型,只有在stocklike=False时起作用
                            margin=None,
                            # 乘数，盈亏会按该乘数进行放大
                            mult=1.0,
                            # 交易费用计算方式，取值有：
                                # 1.CommInfoBase.COMM_PERC 百分比费用
                                # 2.CommInfoBase.COMM_FIXED 固定费用
                                # 3.None 根据 margin 取值来确定类型
                            commtype=None,
                            # 当交易费用处于百分比模式下时，commission 是否为 % 形式
                                # True，表示不以 % 为单位，0.XX 形式；False，表示以 % 为单位，XX% 形式
                            percabs=True,
                            # 是否为股票模式，该模式通常由margin和commtype参数决定
                                # margin=None或COMM_PERC模式时，就会stocklike=True，对应股票手续费；
                                # margin设置了取值或COMM_FIXED模式时,就会stocklike=False，对应期货手续费
                            stocklike=False,
                            # 计算持有的空头头寸的年化利息
                                # days * price * abs(size) * (interest / 365)
                            interest=0.0,
                            # 计算持有的多头头寸的年化利息
                            interest_long=False,
                            # 杠杆比率，交易时按该杠杆调整所需现金
                            leverage=1.0,
                            # 自动计算保证金
                                # 如果False, 则通过margin参数确定保证金
                                # 如果automargin<0, 通过mult*price确定保证金
                                # 如果automargin>0, 如果automargin*price确定保证金
                            automargin=False,
                            # 交易费用设置作用的数据集(也就是作用的标的)
                                # 如果取值为None，则默认作用于所有数据集(也就是作用于所有assets)
                            name=None
                            )

#%%
# 第3.3节 通过 addcommissioninfo() 设置
# 如果想要更灵活的设置交易费用，可以在继承 CommInfoBase 基础类的基础上自定义交易费用子类 ，然后通过 addcommissioninfo() 方法将实例添加进 broker。
'''
Backtrader 中与交易费用相关的设置都是由 CommInfoBase 类管理的，
setcommission() 方法中的参数就是 CommInfoBase 类中 params 属性里包含的参数，
此外还内置许多 getxxx 方法，用于计算并返回交易产生的指标:

    计算成交量 getsize(price, cash) 
    计算持仓市值 getvalue(position, price)
    计算佣金getcommission(size, price) 或 _getcommission(self, size, price, pseudoexec)
    计算保证金 get_margin(price) 

其中自定义时最常涉及的就是上面案例中显示的 _getcommission 和 get_margin
'''

# 在继承 CommInfoBase 基础类的基础上自定义交易费用
class MyCommission(bt.CommInfoBase):
    # 对应 setcommission 中介绍的那些参数，也可以增添新的全局参数
    params = ((xxx, xxx),)
    # 自定义交易费用计算方式
    def _getcommission(self, size, price, pseudoexec):
        pass
    # 自定义佣金计算方式
    def get_margin(self, price):
        pass
    ...
    
# 实例化
mycomm = MyCommission(...)
cerebro = bt.Cerebro()
# 添加进 broker
cerebro.broker.addcommissioninfo(mycomm, name='xxx') # name 用于指定该交易费用函数适用的标的

#%%
# 第3.3.1节 自定义交易费用的例子1：自定义期货百分比费用

# 方法1：通过 setcommission 实现
cerebro.broker.setcommission(commission=0.1, #0.1%
                             mult=10,
                             margin=2000,
                             percabs=False,
                             commtype=bt.CommInfoBase.COMM_PERC,
                             stocklike=False)

# 方法2：通过 addcommissioninfo 实现
class CommInfo_Fut_Perc_Mult(bt.CommInfoBase):
    params = (
                ('stocklike', False), # 指定为期货模式
                ('commtype', bt.CommInfoBase.COMM_PERC), # 使用百分比费用
                ('percabs', False), # commission 以 % 为单位
             )

    def _getcommission(self, size, price, pseudoexec):
        # 计算交易费用
        return (abs(size) * price) * (self.p.commission/100) * self.p.mult
        # pseudoexec 用于提示当前是否在真实统计交易费用：如果只是试算费用，pseudoexec=False；如果是真实的统计费用，pseudoexec=True

comminfo = CommInfo_Fut_Perc_Mult(commission=0.1, # 0.1%
                                  mult=10,
                                  margin=2000) 
                                    

cerebro.broker.addcommissioninfo(comminfo)
#%%
# 第3.3.2节 自定义交易费用的例子2：考虑佣金和印花税的股票百分比费用
class StockCommission(bt.CommInfoBase):
    params = (
                ('stocklike', True), # 指定为股票模式
                ('commtype', bt.CommInfoBase.COMM_PERC), # 使用百分比费用模式
                ('percabs', True), # commission 不以 % 为单位
                ('stamp_duty', 0.001), # 印花税默认为 0.1%
             ) 
    
    # 自定义费用计算公式
    def _getcommission(self, size, price, pseudoexec):
            if size > 0: # 买入时，只考虑佣金
                return abs(size) * price * self.p.commission
            elif size < 0: # 卖出时，同时考虑佣金和印花税
                return abs(size) * price * (self.p.commission + self.p.stamp_duty)
            else:
                return 0

# =============================================================================
#%%
# 第4章 成交量限制管理
'''
默认情况下，Broker 在撮合成交订单时，不会将订单上的购买数量与成交当天 bar 的总成交量 volume 进行对比，
即使购买数量超出了当天该标的的总成交量，也会按购买数量全部撮合成交，显然这种“无限的流动性”是不现实的，
这种 “不考虑成交量，默认全部成交” 的交易模式，也会使得回测结果与真实结果产生较大偏差。

如果想要修改这种默认模式，可以通过 Backtrader 中的 fillers 模块来限制实际成交量，
fillers 会告诉 Broker 在各个成交时间点应该成交多少量，一共有 3 种形式。
'''

# 第4.1节 形式1：bt.broker.fillers.FixedSize(size) 
'''
通过 FixedSize() 方法设置最大的固定成交量：size，该种模式下的成交量限制规则如下：

1. 订单实际成交量的确定规则：取（size、订单执行那天的 volume 、订单中要求的成交数量）中的最小者；
2. 订单执行那天，如果订单中要求的成交数量无法全部满足，则只成交部分数量。
'''
## 方法1：通过 BackBroker() 类直接设置
cerebro = Cerebro()
filler = bt.broker.fillers.FixedSize(size=xxx)
newbroker = bt.broker.BrokerBack(filler=filler)
cerebro.broker = newbroker

## 方法2：通过 set_filler 方法设置
cerebro = Cerebro()
cerebro.broker.set_filler(bt.broker.fillers.FixedSize(size=xxx))

# 输出案例（部分示例代码）
......
self.order = self.buy(size=2000) # 每次买入 2000 股
......
cerebro.broker.set_filler(bt.broker.fillers.FixedSize(size=3000)) # 固定最大成交量

'''
【输出】===================================================================================
情况1：
2019-01-17 这天执行买入订单，当天 volume 869.0 < buy(size=2000) < FixedSize(size=3000)，
所以当天只买入了最小的 volume 869 股，剩余未成交数量 Remsize: 1131.00 ；2019-02-22 这天情况类似；

情况2：
2019-03-15 这天执行买入订单，当天 buy(size=2000) < FixedSize(size=3000)< volume 3063.0，
所以可以全部成交，剩余未成交数量 Remsize: 0；

情况3：
2019-05-20 这天执行卖出订单，当天 close 平仓时的仓位 2000.0 > volume 1686.0，无法全部平仓，
所以只卖出了 1686 股，剩余未成交数量 Remsize: -314.00；
随后，在 2019-06-12 再次触发卖出信号，2019-06-13 执行卖出，对剩余仓位 341 股 进行了平仓。

【结果】===================================================================================
1. 对订单执行当天未成交的剩余数量，并不会在第二天接着成交；

2. 在订单执行当天，如果遇到对于无法全部成交的情况，订单会被部分执行，然后在第二天取消该订单，并打印 notify_order：

    2019-01-16 这一天触发买入信号，下达订单指令，创建订单;
    2019-01-17 订单被传递给 broker，并由 broker 接受，然后由于成交量限制，订单被部分执行;
    2019-01-18 这天，剩余订单会被取消，同时打印 notify_order。
'''

#%%
# 第4.2节 形式2：bt.broker.fillers.FixedBarPerc(perc)
'''
通过 FixedBarPerc(perc) 将 订单执行当天 bar 的总成交量 volume 的 perc % 设置为最大的固定成交量，该模式的成交量限制规则如下：

1. 订单实际成交量的确定规则：取 （volume * perc /100、订单中要求的成交数量）的最小者；
2. 订单执行那天，如果订单中要求的成交数量无法全部满足，则只成交部分数量。
'''

# 方法1：通过 BackBroker() 类直接设置
cerebro = Cerebro()
filler = bt.broker.fillers.FixedBarPerc(perc=xxx)
newbroker = bt.broker.BrokerBack(filler=filler)
cerebro.broker = newbroker

# 方法2：通过 set_filler 方法设置
cerebro = Cerebro()
cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=xxx)) # perc 以 % 为单位，取值范围为[0.0,100.0]

# 输出案例（部分示例代码）
......
self.order = self.buy(size=2000) # 以下一日开盘价买入2000股
......
cerebro.broker.set_filler(bt.broker.fillers.FixedBarPerc(perc=50)) # perc=50 表示 50%

'''
【输出】===================================================================================
情况1：
2019-01-17 这天执行买入订单，订单的buy(size=2000) > 当天 volume 869.0，只能部分成交，
数量为 volume 869.0 * （50/100）= 434 ，订单剩余数量 Remsize: 1566.00 不会成交；2019-02-22 这天情况类似；

情况2：
2019-03-15 这天执行买入订单，当天 buy(size=2000) < volume 3063.0，所以可以全部成交，
剩余未成交数量 Remsize: 0；

情况3：
2019-04-03 这天执行卖出订单，当天要 close 平仓的量仓位为 2000.0 ，虽然小于当天的 volume 3826.0，
但是大于 volume 3826.0 *（50/100）= 1913.00，所以最多只成交了 1913.00，还剩 Remsize: -87.00 未成交；
随后，在 2019-05-17 再次触发卖出信号，2019-05-20 剩余仓位 87 进行了平仓。
'''

#%%
# 第4.3节 形式3：bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)
'''
BarPointPerc() 在考虑了价格区间的基础上确定成交量，在订单执行当天，成交量确定规则为：

1. 通过 minmov 将 当天 bar 的价格区间 low ~ high 进行均匀划分，得到划分的份数：
    part =  (high - low + minmov)  // minmov  （向下取整）


2. 再对当天 bar 的总成交量 volume 也划分成相同的份数 part ，这样就能得到每份的平均成交量：
    volume_per = volume // part 

3. 最终，volume_per * （perc / 100）就是允许的最大成交量，实际成交时，对比订单中要求的成交量，就可以得到最终实际成交量:
    实际成交量 = min ( volume_per * （perc / 100）, 订单中要求的成交数量 )
'''

# 方法1：通过 BackBroker() 类直接设置
cerebro = Cerebro()
filler = bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)
newbroker = bt.broker.BrokerBack(filler=filler)
cerebro.broker = newbroker

# 方法2：通过 set_filler 方法设置
cerebro = Cerebro()
cerebro.broker.set_filler(bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)) # perc 以 % 为单位，取值范围为[0.0,100.0]

# 输出案例（部分示例代码）
......
self.order = self.buy(size=2000) # 以下一日开盘价买入2000股
......
cerebro.broker.set_filler(bt.broker.fillers.BarPointPerc(minmov=0.1, perc=50)) # 表示 50%

'''
【输出】===================================================================================
    part = (high 32.94151482 - low 31.83112668 + minmov 0.1) // minmov 0.1 = 12.0
    volume_per = volume 869.0 // 12.0 = 72.0
    最终成交数量 = min ( volume_per 72.0 * （perc 50 / 100）, 订单中要求的成交数量 2000 ) = 36.0

【结果】原计划买入2000股，结果只能买入36股
'''
# =============================================================================
#%%
# 第5章 交易时机管理
'''
对于交易订单生成和执行时间，Backtrader 默认是 “当日收盘后下单，次日以开盘价成交”，这种模式在回测过程中能有效避免使用未来数据。
但对于一些特殊的交易场景，比如“all_in”情况下，当日所下订单中的数量是用当日收盘价计算的（总资金 / 当日收盘价），
次日以开盘价执行订单时，如果开盘价比昨天的收盘价提高了，就会出现可用资金不足的情况。

为了应对一些特殊交易场景，Backtrader 还提供了一些 cheating 式的交易时机模式：Cheat-On-Open 和 Cheat-On-Close。
'''

# 第5.1节 Cheat-On-Open
'''
Cheat-On-Open：当日下单，当日以开盘价成交

在该模式下，Strategy 中的交易逻辑不再写在 next() 方法里，而是写在特定的 next_open()、nextstart_open() 、prenext_open() 函数中

    方式1：bt.Cerebro(cheat_on_open=True)
    方式2：cerebro.broker.set_coo(True)
    方式3：BackBroker(coo=True)
'''

class TestStrategy(bt.Strategy):
    ......
    def next_open(self):
        # 取消之前未执行的订单
        if self.order:
            self.cancel(self.order)
        # 检查是否有持仓
        if not self.position:
            # 10日均线上穿5日均线，买入
            if self.crossover > 0:
                print('{} Send Buy, open {}'.format(self.data.datetime.date(),self.data.open[0]))
                self.order = self.buy(size=100) # 以下一日开盘价买入100股
        # # 10日均线下穿5日均线，卖出
        elif self.crossover < 0:
            self.order = self.close() # 平仓，以下一日开盘价卖出
    ......

# 方法1：实例化大脑，开启：cheat_on_open
cerebro= bt.Cerebro(cheat_on_open=True)
.......
# 方法2：当日下单，当日开盘价成交
cerebro.broker.set_coo(True)

'''
【结果】===================================================================================
    1. 原本 2019-01-16 生成的下单指令，被延迟到了 2019-01-17 日才发出；
    2. 2019-01-17 发出的订单，在 2019-01-17 当日就以 开盘价 执行成交了。
'''

#%%
# 第5.2节 Cheat-On-Close
'''
Cheat-On-Close：当日下单，当日以收盘价成交

在该模式下，Strategy 中的交易逻辑仍写在 next() 中

    方式1：cerebro.broker.set_coc(True)
    方式2：BackBroker(coc=True)
'''
class TestStrategy(bt.Strategy):
    ......
    def next(self):
        # 取消之前未执行的订单
        if self.order:
            self.cancel(self.order)
        # 检查是否有持仓
        if not self.position:
            # 10日均线上穿5日均线，买入
            if self.crossover > 0:
                print('{} Send Buy, open {}'.format(self.data.datetime.date(),self.data.open[0]))
                self.order = self.buy(size=100) # 以下一日开盘价买入100股
        # # 10日均线下穿5日均线，卖出
        elif self.crossover < 0:
            self.order = self.close() # 平仓，以下一日开盘价卖出
    ......

# 实例化大脑（不能在这里开启Cheat-On-Close）
cerebro= bt.Cerebro()
.......
# 当日下单，当日收盘价成交
cerebro.broker.set_coc(True)

'''
【结果】===================================================================================
    2019-01-16 生成的下单指令，当天就被发送，而且当天就以 收盘价 执行了；并未在指令发出的下一日执行。
'''