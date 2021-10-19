# Backtrader 中文教程
* 作者：[量化投资与机器学习](https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzAxNTc0Mjg0Mg==&scene=124#wechat_redirect)
* 笔记：Jason

## [Lesson1：Backtrader来啦](https://mp.weixin.qq.com/s/7S4AnbUfQy2kCZhuFN1dZw)
Backtrader 是 2015 年开源的 Python 量化回测框架（支持实盘交易），功能丰富，操作方便灵活：
* 品种多：股票、期货、期权、外汇、数字货币；
* 周期全：Ticks 级、秒级、分钟级、日度、周度、月度、年度；
* 速度快：pandas 矢量运算、多策略并行运算；
* 组件多：内置 Ta-lib 技术指标库、PyFlio 分析模块、plot 绘图模块、参数优化等；
* 超灵活：即可以随意搭配组件，又支持扩展自己开发的功能，想怎么玩就怎么玩；
* 社区活跃、帮助文档齐全，官网：https://www.backtrader.com/。

```python
# 若已经安装了 matplotlib ，只需安装 backtrader
pip install backtrader

# 若没有安装 matplotlib，可将其与 backtrader 一起安装
pip install backtrader[plotting]
```

## [Lesson2：Backtrader来啦：数据篇](https://mp.weixin.qq.com/s/NTct2_AYhz4Z8q5MYtBQcA)

### Data Feed 数据馈送对象
* 数据表格中的“行”和“列”
* 列是“lines”
* 如何调用某一条 line ?
* 如何提取 line 上的数据点？
* 行是“Bars”

### DataFeeds 数据模块
* 默认的导入方式
* 自定义读取函数
* 新增指标

## [Lesson3：Backtrader来啦：指标篇](https://mp.weixin.qq.com/s/rFaU96l4mYzC0Kaua9jRJA)
在编写策略时，除了常规的高开低收成交量等行情数据外，还会用到各式各样的指标（变量），比如宏观经济指标、基本面分析指标、技术分析指标、另类数据等等。Backtrader 大致有 2 种获取指标的方式：

    1. 直接通过 DataFeeds 模块导入已经计算好的指标，比如《数据篇》中的导入新增指标 PE、PB；
    2. 在编写策略时调用 Indicators 指标模块临时计算指标，比如 5 日均线、布林带等 。

* 哪些地方会用到指标 ？
* 在`__init__() `中提前计算指标
* 关于 Indicators 返回的指标对象
* 计算指标时的各种简写形式
* 调用指标时的各种简写形式
* 好用的运算函数
* 如何对齐不同周期的指标
* [丰富的内置指标](https://www.backtrader.com/docu/indautoref/)
* 在 Backtrader 中调用 TA-Lib 库
* 自定义新指标

## [Lesson4：Backtrader来啦：交易篇（上）](https://mp.weixin.qq.com/s/30ShvEKmoyP07QBxHXnmUQ)

Backtrader中的交易流程大致如下：

    * step1：设置交易条件：初始资金、交易税费、滑点、成交量限制等；
    * step2：在 Strategy 策略逻辑中下达交易指令 buy、sell、close，或取消交易 cancel；
    * step3：Order 模块会解读交易订单，解读的信息将交由经纪商 Broker 模块处理；
    * step4：经纪商 Broker 会根据订单信息检查订单并确定是否接收订单；
    * step5：经纪商 Broker 接收订单后，会按订单要求撮合成交 trade，并进行成交结算；
    * step6：Order 模块返回经纪商 Broker 中的订单执行结果。

### Broker 中的交易条件
* 资金管理
* 持仓查询

### 滑点管理
* 百分比滑点
* 固定滑点
* 其他设置

### 交易税费管理
* 通过 BackBroker() 设置
* 通过 setcommission() 设置
* 通过 addcommissioninfo() 设置
* 自定义交易费用的例子

### 成交量限制管理
* 形式1：bt.broker.fillers.FixedSize(size) 
* 形式2：bt.broker.fillers.FixedBarPerc(perc)
* 形式3：bt.broker.fillers.BarPointPerc(minmov=0.01，perc=100.0)

### 交易时机管理
* Cheat-On-Open
* Cheat-On-Close


## [Lesson5：Backtrader来啦：交易篇（下）](https://mp.weixin.qq.com/s/CJwSpvS07JLT4xhO19SOeA)

### Order 中的交易订单
* Order.Market
* Order.Close
* Order.Limit
* Order.Stop
* Order.StopLimit
* Order.StopTrail
* Order.StopTrailLimit

### Strategy 中的交易函数
* 常规下单函数
* 目标下单函数
* 取消订单
* 订单组合
    * buy_bracket()
    * sell_bracket()

### 执行逻辑
* 通用逻辑
    * 只当在主订单执行后，止损单和止盈单才会被激活，而且是同时激活；
    * 如果主订单被取消，止盈单和止损单也会被取消；
    * 在止盈单和止损单激活之后，如果取消两者中的任意一个，那另外一个也会被取消。

* OCO订单

### Broker 中的交易执行
* Order.Created：订单已被创建；
* Order.Submitted：订单已被传递给经纪商 Broker；
* Order.Accepted：订单已被经纪商接收；
* Order.Partial：订单已被部分成交；
* Order.Complete：订单已成交；
* Order.Rejected：订单已被经纪商拒绝；
* Order.Margin：执行该订单需要追加保证金，并且先前接受的订单已从系统中删除；
* Order.Cancelled (or Order.Canceled)：确认订单已经被撤销；
* Order.Expired：订单已到期，其已经从系统中删除

## [Lesson6：Backtrader来啦：策略篇](https://mp.weixin.qq.com/s/WBZAt7Uiddu9LjPEqtb7nQ)

* 通过 Strategy 类开发策略
* 基于交易信号直接生成策略
    * 信号指标取值与多空信号对应关系
    * add_signal(signal type, signal class, arg) 中的参数说明
    * 开仓类
    * 平仓类
    * 关于订单累计和订单并发
* 如何返回策略收益评价指标
* 如何对策略进行参数优化


## [Lesson7：Backtrader来啦：可视化篇（重构）](https://mp.weixin.qq.com/s/WA7Dgr_kcZz-WhriHkf4AQ)

### observers 观测器
* 最常用的观测器
* 如何添加 observers
* 如何读取 observers 中的数据
* 自定义 observers

### plot() 图形绘制
* plot() 中的参数
* 局部绘图参数设置
* 部分修改效果

### 基于收益序列进行可视化