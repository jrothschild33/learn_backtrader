# Lesson5：Backtrader来啦：交易篇（下）
# link: https://mp.weixin.qq.com/s/CJwSpvS07JLT4xhO19SOeA

#%%
# 第1章 Order 中的交易订单
'''
Order.Market
    市价单，以当时市场价格成交的订单，不需要自己设定价格。市价单能被快速达成交易，防止踏空，尽快止损/止盈；
    按下一个 Bar （即生成订单的那个交易日的下一个交易日）的开盘价来执行成交；
    例：self.buy(exectype=bt.Order.Market)

Order.Close
    和 Order.Market 类似，也是市价单，只是成交价格不一样；
    按下一个 Bar 的收盘价来执行成交；
    例：self.buy(exectype=bt.Order.Close) 

Order.Limit
    限价单，需要指定成交价格，只有达到指定价格（limit Price）或有更好价格时才会执行，即以指定价或低于指点价买入，以指点价或更高指定价卖出；
    在订单生成后，会通过比较 limit Price 与之后 Bar 的 open\high\low\close 行情数据来判断订单是否成交。
    如果下一个 Bar 的 open 触及到指定价格 limit Price，就以 open 价成交，订单在这个 Bar 的开始阶段就被执行完成；
    如果下一个 Bar 的 open 未触及到指定价格 limit Price，但是 limit Price 位于这个 bar 的价格区间内 （即 low ~  high），就以 limit Price 成交；
    例：self.buy(exectype=bt.Order.Limit, price=price, valid=valid) 

Order.Stop
    止损单，需要指定止损价格（Stop Price），一旦股价突破止损价格，将会以市价单的方式成交；
    在订单生成后，也是通过比较 Stop Price 与之后 Bar 的 open\high\low\close 行情数据来判断订单是否成交。
    如果下一个 Bar 的 open 触及到指定价格 limit Price，就以 open 价成交；
    如果下一个 Bar 的 open 未触及到指定价格 Stop Price，但是 Stop Price 位于这个 bar 的价格区间内 （即 low ~ high），就以 Stop Price 成交；
    例：self.buy(exectype=bt.Order.Stop, price=price, valid=valid) 

Order.StopLimit
    止损限价单，需要指定止损价格（Stop price）和限价（Limit Price），一旦股价达到设置的止损价格，将以限价单的方式下单；
    在下一个 Bar，按 Order.Stop 的逻辑触发订单，然后以 Order.Limit 的逻辑执行订单；
    例：self.buy(exectype=bt.Order.StopLimit, price=price, valid=valid, plimit=plimit)

Order.StopTrail
    跟踪止损订单，是一种止损价格会自动调整的止损单，调整范围通过设置止损价格和市场价格之间的差价来确定。
    差价即可以用金额 trailamount 表示，也可以用市价的百分比 trailpercent  表示；
    如果是通过 buy 下达了买入指令，就会“卖出”一个跟踪止损单，在市场价格上升时，止损价格会随之上升；
    若股价触及止损价格时，会以市价单的形式执行订单；若市场价格下降或保持不变，止损价格会保持不变；
    如果是通过 sell 下达卖出指令，就会“买入”一个跟踪止损单，在市场价格下降时，止损价格会随之下降；
    若股价触及止损价格时，会以市价单的形式执行订单；但是当市场价格上升时，止损价格会保持不变；
    例：self.buy(exectype=bt.Order.StopTrail, price=xxx, trailamount=xxx)

Order.StopTrailLimit
    跟踪止损限价单，是一种止损价格会自动调整的止损限价单，订单中的限价 Limit Price 不会发生变动，
    止损价会发生变动，变动逻辑与上面介绍的跟踪止损订单一致；
    例：self.buy(exectype=bt.Order.StopTrailLimit, plimit=xxx, trailamount=xxx) 
'''

# =============================================================================
#%%
# 第2章 Strategy 中的交易函数

## 第2.1节 常规下单函数

'''
常规下单函数主要有 3 个：买入 buy() 、卖出 sell()、平仓 close()

data（默认: None）：用于指定给哪个数据集（即哪个证券）创建订单，默认为 None，表示给第 1 个数据集（self.datas[0] 、self.data0 对应的证券）创建订单。

size（默认: None）：订单委托数量（正数），默认为 None，表示会自动通过 getsizer 获取 sizer 。

price（默认: None）：订单委托价， None 表示不指定具体的委托价，而是由市场决定最终的成交价，适用于市价单；对于限价单、止损单和止损限价单，price 就是触发订单执行的那个价格 。

plimit（默认: None）：仅适用于 StopLimit 订单，用于指定 StopLimit 订单的限价 Limit Price 为多少。

exectype （默认: None）：执行的订单类型，None 表示按市价单执行，可选的类型有：
    1. Order.Market  市价单，回测时将以下一个 bar 的开盘价执行的市价单；
    2. Order.Close  市价单，回测时将以下一个 bar 的收盘价执行的市价单；
    3. Order.Limit  限价单；
    4. Order.Stop  止损单；
    5. Order.StopLimit  止损现价单；
    6. Order.StopTrail  跟踪止损订单；
    7. Order.StopTrailLimit  跟踪止损限价单。

valid（默认: None）：订单有效期，可选取值有：
    1. None 表示订单在完成成交或被撤销之前一直都有效（aka Good till cancel or match）; 
    2. datetime实例、date 实例、数值形式的日期，表示订单在设置的 date 之前有效，date 之后会被撤销（aka good till date）；
    3. Order.DAY 、0 、imedelta()，表示订单当日有效，未成交的订单将在当日收盘后被自动撤销（aka day order）。

tradeid（默认: None）：当同一资产出现重复交易的时候，通知订单状态更改时，tradeid 会被传递给 Strategy。

**kwargs：通过传入其他参数，生成特定类型的订单 。
'''


class TestStrategy(bt.Strategy):
    def next(self):
        self.order = self.buy( ...) # 买入、做多 long
        self.order = self.sell(...) # 卖出、做空 short
        self.order = self.close(...) # 平仓 cover

#%%
## 第2.2节 目标下单函数

'''
类型：按目标数量下单、按目标金额下单、按目标百分比下单

order_target_size： 按目标数量下单，按“多退少补”的原则，让证券的持仓数量等于设定的目标数量 target ：

                    如果目标数量 target 大于当前持仓数量，则会发出买入订单，补足持仓量，例如：
                        当前持仓量 size=0， 目标持仓量 target=7 -> 买入订单，买入数量 size=7-0=7；
                        当前持仓量 size=3， 目标持仓量 target=7 -> 买入订单，买入数量 size=7-3=4；
                        当前持仓量 size=-3， 目标持仓量 target=7 -> 买入订单，买入数量 size=7-(-3)=10。

                    如果目标数量 target 小于当前持仓数量，则会发出卖出订单，减少持仓量，例如：
                        当前持仓量 size=0，目标持仓量 target=-7 -> 卖出订单，卖出数量 size=0-(-7)=7；
                        当前持仓量 size=3， 目标持仓量 target=-7 -> 卖出订单，卖出数量 size=3-(-7)=10；
                        当前持仓量 size=-3， 目标持仓量 target=-7 -> 卖出订单，卖出数量 size=-3-(-7)=4。


order_target_value：按目标金额下单，通过比较目标金额与当前持仓额和持仓方向，确定最终买卖方向：
                    （持仓量默认使用当前 Bar 的 close 进行计算，然后以下一根 bar 的开盘价进行交易）

                    如果当前持有的是空单（size<0）：
                        若目标金额 target > 当前持仓额 -> 卖出；
                        若目标金额 target < 当前持仓额 -> 买入。

                    如果当前无持仓或持有的是多单（size>=0）：
                        若目标金额 target > 当前持仓额 ->  买入；
                        若目标金额 target < 当前持仓额 ->  卖出。


order_target_percent：按目标百分比下单，订单生成逻辑同 order_target_value，
                      目标金额 = 目标百分比 * 当前账户的总资产。
'''

class TestStrategy(bt.Strategy):
   def next(self):
      # 按目标数量下单
      self.order = self.order_target_size(target=size)
      # 按目标金额下单
      self.order = self.order_target_value(target=value)
      # 按目标百分比下单
      self.order = self.order_target_percent(target=percent)

#%%
## 第2.3节 取消订单
'''
1. 通过 cancel() 来取消订单 ：self.cancel(order)；
2. 通过 Broker 来取消订单 ：self.broker.cancel(order) 
'''

#%%
## 第2.4节 订单组合
'''
订单组合并不是同时对多个标的进行交易，而是对某一笔交易同时发出多个指令，以满足在不同市场情况时触发对应的指令

buy_bracket() 和 sell_bracket() 会一次性生成 3 个自定义类型的订单：
    主订单 main order
    针对主订单的止损单 stop order
    针对主订单的止盈单 limit order 

buy_bracket()
    buy_bracket() 用于long side 的交易场景，
    买入证券后，在价格下跌时，希望通过止损单卖出证券，限制损失；
    在价格上升时，希望通过限价单卖出证券，及时获利。

sell_bracket()
    sell_bracket() 用于short side 的交易场景，
    卖出证券做空后，在价格上升时，希望通过止损单买入证券，限制损失；
    在价格下降时，希望通过限价单买入证券，及时获利

    【参数设置】
    data=None，默认是对 data0 数据集对应的证券标的进行交易；
    主订单：为买入单，默认为 Order.Limit  限价单，可通过参数 price 设定成交价，也可通过参数  plimit 设置指定价 limit；主订单通常设置为 Order.Limit  限价单 或 Order.StopLimit 止损限价单；
    止损单：为卖出单，用于及时止损，默认为 Order.Stop 止损单，可通过参数 stopprice 设置止损价，参数 stopargs 中还可设置止损单相关的其他参数；
    止盈单：为卖出单，用于及时止盈，默认为 Order.Limit 限价单，可通过参数 limitprice 设置指定价格，参数 limitargs 中还可设置限价单相关的其他参数。


【执行逻辑】
    一篮子订单中的三个订单是一块提交的，但执行顺序有主有次、有先有后：
    只当在主订单执行后，止损单和止盈单才会被激活，而且是同时激活；
    如果主订单被取消，止盈单和止损单也会被取消；
    在止盈单和止损单激活之后，如果取消两者中的任意一个，那另外一个也会被取消。
'''
# 函数可用参数
buy_bracket(# 主订单的参数
            data=None, size=None, price=None,
            plimit=None,exectype=bt.Order.Limit,
            valid=None, tradeid=0,
            trailamount=None, trailpercent=None,
            oargs={},
            # 止损单的参数
            stopprice=None, stopexec=bt.Order.Stop, stopargs={},
            # 止盈单的参数
            limitprice=None, limitexec=bt.Order.Limit, limitargs={},
            **kwargs)

# 主订单以 13.5 的价格买入 self.data0 数据集对应的标的
# 当价格超过 14.00 时，会触发止盈单，卖出标的
# 当价格跌破 13.00 时，会触发止损单，卖出标的
brackets = self.buy_bracket(price=13.50,
                            limitprice=14.00,
                            stopprice=13.00)

# 函数可用参数
sell_bracket(# 主订单设置
             data=None,size=None, price=None, plimit=None,
             exectype=bt.Order.Limit, valid=None, tradeid=0,
             trailamount=None, trailpercent=None, oargs={},
             # 止损单设置
             stopprice=None, stopexec=bt.Order.Stop, stopargs={},
             # 止盈单设置
             limitprice=None, limitexec=bt.Order.Limit, limitargs={},
             **kwargs)

# 主订单以 13.5 的价格卖出 self.data0 数据集对应的标的
# 当价格跌破 13.00 时，会触发止盈单，买入标的，获得套利收益
# 当价格超过 14.00 时，会触发止损单，买入标的，及时止损
brackets = self.sell_bracket(price=13.50,
                             limitprice=13.00,
                             stopprice=14.00)

#%%
## 第2.5节 OCO订单
'''
OCO 是“aka One Cancel Others”的缩写，OCO 针对的是多个相互关联的订单，
一个订单的执行、取消或到期（对应的订单状态有：Completed、Cancelled、Margin、Expired），就会自动取消其他与其相关联的订单。
可以将 OCO 看做是订单的属性或特征，通过下单函数中的“oco”参数来设置。

【案例1】
    生成的 o1 与 o2 是一组关联订单，其中 o1 是主订单，它的执行情况将会决定 o2 的生死存亡，
    如果 o1 被执行、取消或到期，就会自动取消订单 o2； 
    o1 与 o3 也是一组关联订单，情况与o1 - o2 组类似；

【案例2】
    订单 o1 关联着订单 o2，订单 o2 关联着订单 o3，
    虽然是 2 组关联订单，实质上o1、o2、o3 是一组订单，
    因为 o1 以 o2 为媒介，影响 o2 的同时，也影响了 o3。
'''

# 案例1
def next(self):
   ...
   o1 = self.buy(...)
   ...
   o2 = self.buy(..., oco=o1)
   ...
   o3 = self.buy(..., oco=o1)

# 案例 2
def next(self):
   ...
   o1 = self.buy(...)
   ...
   o2 = self.buy(..., oco=o1)
   ...
   o3 = self.buy(..., oco=o2)

# =============================================================================
#%%
## 第3章 Broker 中的交易执行
'''
Broker 在执行交易时，会根据执行流程给订单赋予不同的状态，不同阶段的订单状态可以通过Strategy 中定义 notify_order() 方法来捕获，从而进行自定义的处理，从下达交易指令到订单执行结束，订单可能会依次呈现如下状态：
    Order.Created：订单已被创建；
    Order.Submitted：订单已被传递给经纪商 Broker；
    Order.Accepted：订单已被经纪商接收；
    Order.Partial：订单已被部分成交；
    Order.Complete：订单已成交；
    Order.Cancelled (or Order.Canceled)：确认订单已经被撤销；
    Order.Expired：订单已到期，其已经从系统中删除；
    Order.Margin：执行该订单需要追加保证金，并且先前接受的订单已从系统中删除；
    Order.Rejected：订单已被经纪商拒绝；
    
上述状态的排列顺序依次为：
    Created：0，已创建
    Submitted：1，已提交
    Accepted：2，已接收
    Partial：3，部分完成
    Completed：4，已完成
    Canceled：5，已取消
    Expired：6，已过期
    Margin：7，需要追加保证金
    Rejected：8，已拒绝
order.status 的取值对应上述专题的位置索引，如order.status==4，对应 'Completed' 状态 。  
'''