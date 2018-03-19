# coding=utf-8
import numpy as np
import statsmodels.api as sm
from pyalgotrade.dataseries import aligned
from pyalgotrade import strategy,broker, bar
from pyalgotrade.stratanalyzer import returns, sharpe, drawdown, trades
from pyalgotrade.utils import stats
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from enum import Enum,unique
from WindPy import *
from webapp.Library.wind import WindData_to_DataFrame
from webapp.Library.pyalgotrade_custom import dataFramefeed,plotter,positionRecord
from webapp.Library.process_bar import ShowProcess
import tushare as ts
<<<<<<< HEAD
import base64,datetime

=======
import base64,datetime,time
>>>>>>> 78c34cb1f3470e97847f449bbb5ace50d08552fa
def handle_form(form):
    type=form.get('type')
    if type=="Pair_Strategy_Based_Bank":
        mystr = Strategy_Manager(Strategy.Pair_Strategy_Based_Bank, commission=float(form.get('commission')), cash=float(form.get('cash')),
                                 instrument_1=form.get('instrument_1'), instrument_2=form.get('instrument_2'), startdate=form.get('sdate'), enddate=form.get('edate'))
        mystr.run()
        return mystr.getResult()
    if type=="DoubleMA_Strategy":
        mystr = Strategy_Manager(Strategy.DoubleMA_Strategy,commission=float(form.get('commission')), cash=float(form.get('cash')), instrument=form.get('instrument'),
                                 startdate=form.get('sdate'), enddate=form.get('edate'))
        mystr.run()
        return mystr.getResult()
<<<<<<< HEAD
=======
    if type=="Stock_Picking_Strategy_Based_Value_By_Steve_A":
        mystr = Strategy_Manager(Strategy.Stock_Picking_Strategy_Based_Value_By_Steve_A, commission=float(form.get('commission')),
                                 cash=float(form.get('cash')),startdate=form.get('sdate'), enddate=form.get('edate'))
        mystr.run()
        return mystr.getResult()
>>>>>>> 78c34cb1f3470e97847f449bbb5ace50d08552fa

def handle_liveform(form):
    type=form.get('type')
    if type=="Pair_Strategy_Based_Bank":
        params={"commission":float(form.get('commission')), "cash":float(form.get('cash')),"instrument_1":form.get('instrument_1'), "instrument_2":form.get('instrument_2')}
        data={"strategy_id":Strategy.Pair_Strategy_Based_Bank.value,"strategy_name":form.get('strategy_name'),"params":params,"build_date":datetime.datetime.now()}
        return data
    if type=="DoubleMA_Strategy":
        params = {"commission": float(form.get('commission')), "cash": float(form.get('cash')),
                  "instrument": form.get('instrument')}
        data = {"strategy_id": Strategy.DoubleMA_Strategy.value, "strategy_name": form.get('strategy_name'),
                "params": params, "build_date": datetime.datetime.now()}
        return data
    if type=="Buy_Everyday":
        params = {"commission": float(form.get('commission')), "cash": float(form.get('cash')),
                  "instrument": form.get('instrument')}
        data = {"strategy_id": Strategy.Buy_Everyday.value, "strategy_name": form.get('strategy_name'),
                "params": params, "build_date": datetime.datetime.now()}
        return data

def dict_to_sql(dict):
    tempstr=str(dict)
    binary=base64.b64encode(tempstr)
    return binary

def sql_to_dict(bin):
    tempstr=base64.b64decode(bin)
    dict=eval(tempstr)
    return dict

def create_position_records_DataCalculator(order,position_record):
    for i in position_record:
        if i.code==order.code:
            return i
    return False

def create_position_records(history):
    history.reverse()
    position_records=[]
    for o in history:
        if o.position=='buy':
            flag=create_position_records_DataCalculator(o,position_records)
            if flag:
                flag.total_cost = (flag.total_cost * flag.shares + (o.price * o.amount + o.commission)) / (flag.shares + o.amount)  # average cost per share
                flag.shares = flag.shares + o.amount
            else:
                #没有
                cost=(o.price * o.amount + o.commission)/ o.amount  # average cost per share
                record=positionRecord.positionRecord(o.code,o.amount,cost)
                position_records.append(record)
        if o.position=='sell':
            flag = create_position_records_DataCalculator(o, position_records)
            if flag:
                if flag.shares==o.amount:
                    position_records.remove(flag)
                if flag.shares > o.amount:
                    flag.total_cost = (flag.total_cost * flag.shares - (o.price * o.amount + o.commission)) / (flag.shares - o.amount)
                    flag.shares = flag.shares - o.amount
    return position_records

@unique
class Strategy(Enum):
    Pair_Strategy_Based_Bank = 0  # 设置sun 的value为  策略id 数据库
    DoubleMA_Strategy=1
    Buy_Everyday=2
    Stock_Picking_Strategy_Based_Value_By_Steve_A=3
    # Sat = 6 # 如果重复会报错 TypeError: Attempted to reuse key: 'Sat'
    # @unique装饰器可以帮助我们检查保证没有重复值

# 策略管理器 当前为变量传递问题未解决的写法 已经解决了传值问题 以后采用新的传值方式，不再使用self.__来保存变量 直接传递到函数 善用解铃 系铃

class Strategy_Manager():
    def __init__(self, StrategyType,live=False,**args):
        self.__strategy_type = StrategyType
        self.__live=live
        if StrategyType == Strategy.Pair_Strategy_Based_Bank:
            if self.__live:
                self.__commission = args.get('commission')
                self.__builddate = args.get('builddate')
                self.__cash = args.get('cash')
                self.__i1 = args.get('instrument_1')
                self.__i2 = args.get('instrument_2')
                self.__init_Pair_Strategy_Based_Bank_Live()
            else:
                self.__commission = args.get('commission')
                self.__startdate = args.get('startdate')
                self.__enddate = args.get('enddate')
                self.__cash = args.get('cash')
                self.__i1 = args.get('instrument_1')
                self.__i2 = args.get('instrument_2')
                self.__init_Pair_Strategy_Based_Bank()

        if StrategyType==Strategy.DoubleMA_Strategy:
            if self.__live:
                self.__commission = args.get('commission')
                self.__builddate = args.get('builddate')
                self.__cash = args.get('cash')
                self.__i = args.get('instrument')
                self.__init_DoubleMA_Strategy_Live()
            else:
                self.__commission = args.get('commission')
                self.__startdate = args.get('startdate')
                self.__enddate = args.get('enddate')
                self.__cash = args.get('cash')
                self.__i = args.get('instrument')
                self.__init_DoubleMA_Strategy()

        if StrategyType==Strategy.Buy_Everyday:
            self.__commission = args.get('commission')
            self.__builddate = args.get('builddate')
            self.__cash = args.get('cash')
            self.__i = args.get('instrument')
            self.__init_Buy_Everyday_Live()

        if StrategyType==Strategy.Stock_Picking_Strategy_Based_Value_By_Steve_A:
            if self.__live:
                pass
            else:
                self.__commission = args.get('commission')
                self.__startdate = args.get('startdate')
                self.__enddate = args.get('enddate')
                self.__cash = args.get('cash')
                self.__init_Stock_Picking_Strategy_Based_Value_By_Steve_A()


    def __init_Pair_Strategy_Based_Bank(self):
        i1_data = ts.get_k_data(self.__i1, (datetime.datetime.strptime(self.__startdate, "%Y-%m-%d")+datetime.timedelta(days=-90)).strftime("%Y-%m-%d"), self.__enddate)
        i2_data = ts.get_k_data(self.__i2, (datetime.datetime.strptime(self.__startdate, "%Y-%m-%d")+datetime.timedelta(days=-90)).strftime("%Y-%m-%d"), self.__enddate)
        feed = dataFramefeed.Feed(bar.Frequency.DAY)
        feed.addBarsFromDataFrame(self.__i1, i1_data)
        feed.addBarsFromDataFrame(self.__i2, i2_data)

        broker_commission = broker.backtesting.TradePercentage(self.__commission)  # 费率交易金额百分比 也可设置固定费率 无手续费
        # 3.2 fill strategy设置
        fill_stra = broker.fillstrategy.DefaultStrategy(volumeLimit=0.1)  # 成交比例 也可以用set方法修改 初始化赋值也可
        sli_stra = broker.slippage.NoSlippage()  # 滑点模型  此为无滑点
        # broker.slippage.VolumeShareSlippage(priceImpact=0.1) 设置影响程度
        fill_stra.setSlippageModel(sli_stra)
        # setVolumeLimit(volumeLimit)  更改成交比例
        # 3.3完善broker类
        brk = broker.backtesting.Broker(self.__cash, feed, broker_commission)  # 初始化
        brk.setFillStrategy(fill_stra)  # 将成交策略传给brk
        # 4.把策略跑起来
<<<<<<< HEAD
        self.__strategy_entity = Pair_Strategy_Based_Bank(feed, brk, self.__i1, self.__i2, 50)
=======
        self.__strategy_entity = Pair_Strategy_Based_Bank(feed, brk, self.__i1, self.__i2, self.__startdate,50)

>>>>>>> 78c34cb1f3470e97847f449bbb5ace50d08552fa
        self.__retAnalyzer = returns.Returns()
        self.__strategy_entity.attachAnalyzer(self.__retAnalyzer)
        self.__sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.__strategy_entity.attachAnalyzer(self.__sharpeRatioAnalyzer)
        self.__drawdownAnalyzer = drawdown.DrawDown()
        self.__strategy_entity.attachAnalyzer(self.__drawdownAnalyzer)
        self.__tradeAnalyzer = trades.Trades()
        self.__strategy_entity.attachAnalyzer(self.__tradeAnalyzer)
        # 绘图模块
        self.__plt = plotter.StrategyPlotter(self.__strategy_entity)

    def __init_Pair_Strategy_Based_Bank_Live(self):
        # i1_data = ts.get_k_data(self.__i1, (self.__builddate+ datetime.timedelta(days=-90)).strftime("%Y-%m-%d"))
        # i2_data = ts.get_k_data(self.__i2, (self.__builddate+ datetime.timedelta(days=-90)).strftime("%Y-%m-%d"))
        i1_data = ts.get_k_data(self.__i1)
        i2_data = ts.get_k_data(self.__i2)
        feed = dataFramefeed.Feed(bar.Frequency.DAY)
        feed.addBarsFromDataFrame(self.__i1, i1_data)
        feed.addBarsFromDataFrame(self.__i2, i2_data)

        broker_commission = broker.backtesting.TradePercentage(self.__commission)  # 费率交易金额百分比 也可设置固定费率 无手续费
        # 3.2 fill strategy设置
        fill_stra = broker.fillstrategy.DefaultStrategy(volumeLimit=0.1)  # 成交比例 也可以用set方法修改 初始化赋值也可
        sli_stra = broker.slippage.NoSlippage()  # 滑点模型  此为无滑点
        # broker.slippage.VolumeShareSlippage(priceImpact=0.1) 设置影响程度
        fill_stra.setSlippageModel(sli_stra)
        # setVolumeLimit(volumeLimit)  更改成交比例
        # 3.3完善broker类
        brk = broker.backtesting.Broker(self.__cash, feed, broker_commission)  # 初始化
        brk.setFillStrategy(fill_stra)  # 将成交策略传给brk
        # 4.把策略跑起来
        self.__strategy_entity = Pair_Strategy_Based_Bank_Live(feed, brk, self.__i1, self.__i2, self.__builddate,50)

        self.__retAnalyzer = returns.Returns()
        self.__strategy_entity.attachAnalyzer(self.__retAnalyzer)
        self.__sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.__strategy_entity.attachAnalyzer(self.__sharpeRatioAnalyzer)
        self.__drawdownAnalyzer = drawdown.DrawDown()
        self.__strategy_entity.attachAnalyzer(self.__drawdownAnalyzer)
        self.__tradeAnalyzer = trades.Trades()
        self.__strategy_entity.attachAnalyzer(self.__tradeAnalyzer)
        # 绘图模块
        self.__plt = plotter.StrategyPlotter(self.__strategy_entity)

    def __init_DoubleMA_Strategy(self):
        i_data = ts.get_k_data(self.__i, (datetime.datetime.strptime(self.__startdate, "%Y-%m-%d")+datetime.timedelta(days=-90)).strftime("%Y-%m-%d"), self.__enddate)
        feed = dataFramefeed.Feed(bar.Frequency.DAY)
        feed.addBarsFromDataFrame(self.__i, i_data)
        broker_commission = broker.backtesting.TradePercentage(self.__commission)  # 费率交易金额百分比 也可设置固定费率 无手续费
        # 3.2 fill strategy设置
        fill_stra = broker.fillstrategy.DefaultStrategy(volumeLimit=0.1)  # 成交比例 也可以用set方法修改 初始化赋值也可
        sli_stra = broker.slippage.NoSlippage()  # 滑点模型  此为无滑点
        # broker.slippage.VolumeShareSlippage(priceImpact=0.1) 设置影响程度
        fill_stra.setSlippageModel(sli_stra)
        # setVolumeLimit(volumeLimit)  更改成交比例
        # 3.3完善broker类
        brk = broker.backtesting.Broker(self.__cash, feed, broker_commission)  # 初始化
        brk.setFillStrategy(fill_stra)  # 将成交策略传给brk
        # 4.把策略跑起来
        self.__strategy_entity = DoubleMA_Strategy(feed, brk, self.__i,self.__startdate,5,20)

        self.__retAnalyzer = returns.Returns()
        self.__strategy_entity.attachAnalyzer(self.__retAnalyzer)
        self.__sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.__strategy_entity.attachAnalyzer(self.__sharpeRatioAnalyzer)
        self.__drawdownAnalyzer = drawdown.DrawDown()
        self.__strategy_entity.attachAnalyzer(self.__drawdownAnalyzer)
        self.__tradeAnalyzer = trades.Trades()
        self.__strategy_entity.attachAnalyzer(self.__tradeAnalyzer)
        # 绘图模块
        self.__plt = plotter.StrategyPlotter(self.__strategy_entity)

    def __init_DoubleMA_Strategy_Live(self):
        # i_data = ts.get_k_data(self.__i, (self.__builddate+ datetime.timedelta(days=-90)).strftime("%Y-%m-%d"))
        i_data = ts.get_k_data(self.__i)
        feed = dataFramefeed.Feed(bar.Frequency.DAY)
        feed.addBarsFromDataFrame(self.__i, i_data)
        broker_commission = broker.backtesting.TradePercentage(self.__commission)  # 费率交易金额百分比 也可设置固定费率 无手续费
        # 3.2 fill strategy设置
        fill_stra = broker.fillstrategy.DefaultStrategy(volumeLimit=0.1)  # 成交比例 也可以用set方法修改 初始化赋值也可
        sli_stra = broker.slippage.NoSlippage()  # 滑点模型  此为无滑点
        # broker.slippage.VolumeShareSlippage(priceImpact=0.1) 设置影响程度
        fill_stra.setSlippageModel(sli_stra)
        # setVolumeLimit(volumeLimit)  更改成交比例
        # 3.3完善broker类
        brk = broker.backtesting.Broker(self.__cash, feed, broker_commission)  # 初始化
        brk.setFillStrategy(fill_stra)  # 将成交策略传给brk
        # 4.把策略跑起来
        self.__strategy_entity = DoubleMA_Strategy_Live(feed, brk, self.__i,self.__builddate,5,20)

        self.__retAnalyzer = returns.Returns()
        self.__strategy_entity.attachAnalyzer(self.__retAnalyzer)
        self.__sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.__strategy_entity.attachAnalyzer(self.__sharpeRatioAnalyzer)
        self.__drawdownAnalyzer = drawdown.DrawDown()
        self.__strategy_entity.attachAnalyzer(self.__drawdownAnalyzer)
        self.__tradeAnalyzer = trades.Trades()
        self.__strategy_entity.attachAnalyzer(self.__tradeAnalyzer)
        # 绘图模块
        self.__plt = plotter.StrategyPlotter(self.__strategy_entity)

    def __init_Buy_Everyday_Live(self):
        # i_data = ts.get_k_data(self.__i, (self.__builddate+ datetime.timedelta(days=-90)).strftime("%Y-%m-%d"))
        i_data = ts.get_k_data(self.__i)
        feed = dataFramefeed.Feed(bar.Frequency.DAY)
        feed.addBarsFromDataFrame(self.__i, i_data)
        broker_commission = broker.backtesting.TradePercentage(self.__commission)  # 费率交易金额百分比 也可设置固定费率 无手续费
        # 3.2 fill strategy设置
        fill_stra = broker.fillstrategy.DefaultStrategy(volumeLimit=0.1)  # 成交比例 也可以用set方法修改 初始化赋值也可
        sli_stra = broker.slippage.NoSlippage()  # 滑点模型  此为无滑点
        # broker.slippage.VolumeShareSlippage(priceImpact=0.1) 设置影响程度
        fill_stra.setSlippageModel(sli_stra)
        # setVolumeLimit(volumeLimit)  更改成交比例
        # 3.3完善broker类
        brk = broker.backtesting.Broker(self.__cash, feed, broker_commission)  # 初始化
        brk.setFillStrategy(fill_stra)  # 将成交策略传给brk
        # 4.把策略跑起来
        self.__strategy_entity = Buy_Everyday_Live(feed, brk, self.__i,self.__builddate)
        self.__retAnalyzer = returns.Returns()
        self.__strategy_entity.attachAnalyzer(self.__retAnalyzer)
        self.__sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.__strategy_entity.attachAnalyzer(self.__sharpeRatioAnalyzer)
        self.__drawdownAnalyzer = drawdown.DrawDown()
        self.__strategy_entity.attachAnalyzer(self.__drawdownAnalyzer)
        self.__tradeAnalyzer = trades.Trades()
        self.__strategy_entity.attachAnalyzer(self.__tradeAnalyzer)
        # 绘图模块
        self.__plt = plotter.StrategyPlotter(self.__strategy_entity)

    def __init_Stock_Picking_Strategy_Based_Value_By_Steve_A(self):
        feed = dataFramefeed.Feed(bar.Frequency.DAY)
        data=w.wset("sectorconstituent", "date="+ self.__startdate +";sectorid=a001010100000000")
        stock_list=data.Data[1][0:20]
        self.__process_bar = ShowProcess(len(stock_list))
        for stock in stock_list:
            stock_data=w.wsd(stock, "open,high,low,close,volume", self.__startdate, self.__enddate, "")
            self.__time_period=len(stock_data.Times)
            feed.addBarsFromDataFrame(stock, WindData_to_DataFrame(stock_data))
            self.__process_bar.show_process()
        self.__process_bar.close()
        broker_commission = broker.backtesting.TradePercentage(self.__commission)  # 费率交易金额百分比 也可设置固定费率 无手续费
        # 3.2 fill strategy设置
        fill_stra = broker.fillstrategy.DefaultStrategy(volumeLimit=0.1)  # 成交比例 也可以用set方法修改 初始化赋值也可
        sli_stra = broker.slippage.NoSlippage()  # 滑点模型  此为无滑点
        # broker.slippage.VolumeShareSlippage(priceImpact=0.1) 设置影响程度
        fill_stra.setSlippageModel(sli_stra)
        # setVolumeLimit(volumeLimit)  更改成交比例
        # 3.3完善broker类
        brk = broker.backtesting.Broker(self.__cash, feed, broker_commission)  # 初始化
        brk.setFillStrategy(fill_stra)  # 将成交策略传给brk
        # 4.把策略跑起来
        self.__strategy_entity = Stock_Picking_Strategy_Based_Value_By_Steve_A(feed, brk,self.__startdate,self.__time_period)

        self.__retAnalyzer = returns.Returns()
        self.__strategy_entity.attachAnalyzer(self.__retAnalyzer)
        self.__sharpeRatioAnalyzer = sharpe.SharpeRatio()
        self.__strategy_entity.attachAnalyzer(self.__sharpeRatioAnalyzer)
        self.__drawdownAnalyzer = drawdown.DrawDown()
        self.__strategy_entity.attachAnalyzer(self.__drawdownAnalyzer)
        self.__tradeAnalyzer = trades.Trades()
        self.__strategy_entity.attachAnalyzer(self.__tradeAnalyzer)
        # 绘图模块
        self.__plt = plotter.StrategyPlotter(self.__strategy_entity)


    def run(self):
        self.__strategy_entity.run()
    def getMessage(self):
        return  self.__strategy_entity.getTextlist()

    def getResult_print(self):
        self.__broker=self.__strategy_entity.getBroker()
        print "市净值: $%.2f" % self.__strategy_entity.getResult()
        print "累计收益率: %.4f " % (self.__retAnalyzer.getCumulativeReturns()[-1])
        print "平均日收益率: %.4f " % (stats.mean(self.__retAnalyzer.getReturns()))
        print "日收益率 标准差: %.4f" % (stats.stddev(self.__retAnalyzer.getReturns()))
        print "夏普率: %.2f" % (self.__sharpeRatioAnalyzer.getSharpeRatio(0))
        print "the duration of the longest drawdown %s" % (self.__drawdownAnalyzer.getLongestDrawDownDuration())
        print "the max. (deepest) drawdown 净资产的最大下降 最大回撤 %.4f" % (self.__drawdownAnalyzer.getMaxDrawDown())
        print "总交易次数 %i" % (self.__tradeAnalyzer.getCount())
        print "盈利交易次数 %i" % (self.__tradeAnalyzer.getProfitableCount())
        print "亏损交易次数 %i" % (self.__tradeAnalyzer.getUnprofitableCount())
        print "不赚不亏的交易次数 %i" % (self.__tradeAnalyzer.getEvenCount())
        print "每次交易盈亏"
        print  self.__tradeAnalyzer.getAll()
        print "每次盈利交易盈利"
        print  self.__tradeAnalyzer.getProfits()
        print "每次亏损交易亏损"
        print self.__tradeAnalyzer.getLosses()
        print "每次交易的收益率"
        print self.__tradeAnalyzer.getAllReturns()
        print "每次盈利交易的收益率"
        print self.__tradeAnalyzer.getPositiveReturns()
        print "每次亏损交易的亏损率"
        print self.__tradeAnalyzer.getNegativeReturns()
        print "每次交易的手续费"
        print self.__tradeAnalyzer.getCommissionsForAllTrades()
        print "每次盈利交易的手续费"
        print self.__tradeAnalyzer.getCommissionsForProfitableTrades()
        print "每次亏损交易的手续费"
        print self.__tradeAnalyzer.getCommissionsForUnprofitableTrades()
        print "每次不赢不亏交易的手续费"
        print self.__tradeAnalyzer.getCommissionsForEvenTrades()
        print "可用现金 %.2f" % (self.__broker.getCash())
        print "持仓情况"
        print self.__broker.getPositions()
        print "持仓数量"
        print self.__broker.getShares("a")  #默认不使用
        print "active order 活跃订单 未完成 已挂出 未完成交易"
        print self.__broker.getActiveOrders()
        self.__plt.plot()

    def getResult(self):
        self.__broker = self.__strategy_entity.getBroker()
        result={}
        result.setdefault('portfolio',self.__strategy_entity.getResult())
        #print "市净值: $%.2f" %
        result.setdefault('culrtn',self.__retAnalyzer.getCumulativeReturns()[-1])
        # print "累计收益率: %.4f " % ()
        result.setdefault('meanrtn',stats.mean(self.__retAnalyzer.getReturns()))
        # print "平均日收益率: %.4f " % ()
        result.setdefault('stdrtn',stats.stddev(self.__retAnalyzer.getReturns()))
        # print "日收益率 标准差: %.4f" % ()
        result.setdefault('sharp',self.__sharpeRatioAnalyzer.getSharpeRatio(0))
        # print "夏普率: %.2f" % ()
        result.setdefault('period',str(self.__drawdownAnalyzer.getLongestDrawDownDuration()))
        # print "the duration of the longest drawdown %s" % ()
        result.setdefault('MDD',self.__drawdownAnalyzer.getMaxDrawDown())
        # print "the max. (deepest) drawdown 净资产的最大下降 最大回撤 %.4f" % ()
        result.setdefault('stimes', self.__tradeAnalyzer.getCount())
        # print "总交易次数 %i" % ()
        result.setdefault('gtimes', self.__tradeAnalyzer.getProfitableCount())
        # print "盈利交易次数 %i" % ()
        result.setdefault('ltimes', self.__tradeAnalyzer.getUnprofitableCount())
        # print "亏损交易次数 %i" % ()
        result.setdefault('btimes', self.__tradeAnalyzer.getEvenCount())
        # print "不赚不亏的交易次数 %i" % ()
        # print "每次交易盈亏"
        result.setdefault('tradeall', list(self.__tradeAnalyzer.getAll()))

        # print "每次盈利交易盈利"
        result.setdefault('tradeg', list(self.__tradeAnalyzer.getProfits()))
        # print "每次亏损交易亏损"
        result.setdefault('tradel', list(self.__tradeAnalyzer.getLosses()))
        # print "每次交易的收益率"
        result.setdefault('rtnall', list(self.__tradeAnalyzer.getAllReturns()))
        # print "每次盈利交易的收益率"
        result.setdefault('rtng', list(self.__tradeAnalyzer.getPositiveReturns()))
        # print "每次亏损交易的亏损率"
        result.setdefault('rtnl', list(self.__tradeAnalyzer.getNegativeReturns()))
        # print "每次交易的手续费"
        result.setdefault('comall', list(self.__tradeAnalyzer.getCommissionsForAllTrades()))
        # print "每次盈利交易的手续费"
        result.setdefault('comg', list(self.__tradeAnalyzer.getCommissionsForProfitableTrades()))
        # print "每次亏损交易的手续费"
        result.setdefault('coml', list(self.__tradeAnalyzer.getCommissionsForUnprofitableTrades()))
        # print "每次不赢不亏交易的手续费"
        result.setdefault('comb', list(self.__tradeAnalyzer.getCommissionsForEvenTrades()))
        result.setdefault('cash', self.__broker.getCash())
        # print "可用现金 %.2f" % ()
        # print "持仓情况"
        result.setdefault('position', self.__broker.getPositions())
        # print "持仓数量"
        # print self.__broker.getShares("a")  # 默认不使用
        # print "active order 活跃订单 未完成 已挂出 未完成交易"
        # print self.__broker.getActiveOrders()
        # self.__plt.plot()
        result.setdefault("chartdata_portfolio",self.__plt.getPortfolio())
        return result,self.__plt.getTradehistory()

def regression(ylist, xlist):  # 回归计算 返回参数 输入类型nparray 返回数组
    xlist = sm.add_constant(xlist)
    model = sm.OLS(ylist, xlist)
    result = model.fit()
    return result.params

def count_shares(number):
    if number>=100:
        return int(number)
    else:
        return 0

def get_last_quarter_date(date):
    today_date=datetime.datetime.strptime(date,"%Y-%m-%d").date()
    cur_year=today_date.year
    cur_month=today_date.month
    cur_day=today_date.day
    first=datetime.date(cur_year,3,31)
    second=datetime.date(cur_year,6,30)
    third=datetime.date(cur_year,9,30)
    forth=datetime.date(cur_year,12,31)
    if today_date==first:
        return date
    if today_date==second:
        return date
    if today_date==third:
        return date
    if today_date==forth:
        return date
    if cur_month<=3:
        return datetime.date(cur_year-1,12,31).strftime("%Y-%m-%d")
    if cur_month<=6:
        return first.strftime("%Y-%m-%d")
    if cur_month<=9:
        return second.strftime("%Y-%m-%d")
    if cur_month<=12:
        return third.strftime("%Y-%m-%d")

class DataCalculator_For_Pair_Strategy_Based_Bank():
    def __init__(self, ds1, ds2, interval):
        # We're going to use datetime aligned versions of the dataseries.
        self.__ds1, self.__ds2 = aligned.datetime_aligned(ds1, ds2) #对齐时间轴
        self.__interval = interval
        self.__a = None
        self.__b = None
        self.__c = None
        self.__d = None
        self.__threshold = None
        self.__params_1 = None
        self.__params_2 = None

    def getThreshold(self):
        return self.__threshold

    def update(self):
        if len(self.__ds1) >= self.__interval:
            values1 = np.asarray(self.__ds1[-1 * self.__interval:])
            values2 = np.asarray(self.__ds2[-1 * self.__interval:])
            self.__params_1 = regression(values2, values1)
            self.__params_2 = regression(values1, values2)
            error_1 = self.__ds1[-1] - (self.__params_2[1] * self.__ds2[-1] + self.__params_2[0])
            error_2 = self.__ds2[-1] - (self.__params_1[1] * self.__ds1[-1] + self.__params_1[0])
            self.__threshold = error_1 - error_2

class Pair_Strategy_Based_Bank(strategy.BacktestingStrategy):
    def __init__(self, feed, brk, instrument1, instrument2, startdate,interval):
        super(Pair_Strategy_Based_Bank, self).__init__(feed, brk)
        self.__DataCalculator = DataCalculator_For_Pair_Strategy_Based_Bank(feed[instrument1].getAdjCloseDataSeries(),
                                                                            feed[instrument2].getAdjCloseDataSeries(),
                                                                            interval)
        self.__startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
        self.__i1 = instrument1
        self.__i2 = instrument2
        self.__thresholdStd = 0
        self.__position = None

    def buyUseAllMoney(self, instrument, bars):
        cash = self.getBroker().getCash(False)
        print cash
        price = bars[instrument].getPrice()
        volume=count_shares(cash / price)
        print 'volume'+ str(volume)
        if volume != 0:
            self.enterLongLimit(instrument, price, volume)

    def onEnterOk(self, position):
        # print position.getEntryOrder().getAction()
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Trade %.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
<<<<<<< HEAD
        self.__DataCalculator.update()  # 计算所有需要指标
        if bars.getBar(self.__i1) and bars.getBar(self.__i2):
            threshold = self.__DataCalculator.getThreshold()
            if threshold is not None:
                currentPos_i1 = self.getBroker().getShares(self.__i1)
                currentPos_i2 = self.getBroker().getShares(self.__i2)
                if threshold < -1 * self.__thresholdStd:
                    if currentPos_i2 > 0:
                        self.enterShort(self.__i2, currentPos_i2)
                    self.buyUseAllMoney(self.__i1, bars)
                elif threshold > self.__thresholdStd:  # Buy spread when its value drops below 2 standard deviations.
                    if currentPos_i1 > 0:
                        self.enterShort(self.__i1, currentPos_i1)
                    self.buyUseAllMoney(self.__i2, bars)
=======
        if bars.getDateTime() >= self.__startdate:
            self.__DataCalculator.update()  # 计算所有需要指标
            if bars.getBar(self.__i1) and bars.getBar(self.__i2):
                threshold = self.__DataCalculator.getThreshold()
                if threshold is not None:
                    currentPos_i1 = self.getBroker().getShares(self.__i1)
                    currentPos_i2 = self.getBroker().getShares(self.__i2)
                    if threshold < -1 * self.__thresholdStd:
                        if currentPos_i2 > 0:
                            self.enterShort(self.__i2, currentPos_i2)
                        self.buyUseAllMoney(self.__i1, bars)
                    elif threshold > self.__thresholdStd:  # Buy spread when its value drops below 2 standard deviations.
                        if currentPos_i1 > 0:
                            self.enterShort(self.__i1, currentPos_i1)
                        self.buyUseAllMoney(self.__i2, bars)
        else:
            pass
>>>>>>> 78c34cb1f3470e97847f449bbb5ace50d08552fa

class Pair_Strategy_Based_Bank_Live(strategy.BacktestingStrategy):
    def __init__(self, feed, brk, instrument1, instrument2, builddate,interval):
        super(Pair_Strategy_Based_Bank_Live, self).__init__(feed, brk)
        self.__DataCalculator = DataCalculator_For_Pair_Strategy_Based_Bank(feed[instrument1].getAdjCloseDataSeries(),
                                                                            feed[instrument2].getAdjCloseDataSeries(),
                                                                            interval)
        self.__i1 = instrument1
        self.__i2 = instrument2
        self.__builddate=builddate
        self.__thresholdStd = 0
        self.__position = None
        self.__text=""
        self.__textlist={}

    def buyUseAllMoney(self, instrument, bars):
        cash = self.getBroker().getCash(False)
        price = bars[instrument].getPrice()
        volume = count_shares(cash / price)
        if volume != 0:
            self.enterLongLimit(instrument, price,volume)
            self.__text+=u"买入"+self.__i1+u"股票"+str(volume)+u"股"

    def getTextlist(self):
        return self.__textlist

    def onEnterOk(self, position):
        # print position.getEntryOrder().getAction()
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Trade %.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        if bars.getDateTime() > self.__builddate:
            self.__text=""
            self.__DataCalculator.update()  # 计算所有需要指标
            if bars.getBar(self.__i1) and bars.getBar(self.__i2):
                threshold = self.__DataCalculator.getThreshold()
                if threshold is not None:
                    currentPos_i1 = self.getBroker().getShares(self.__i1)
                    currentPos_i2 = self.getBroker().getShares(self.__i2)
                    if threshold < -1 * self.__thresholdStd:
                        if currentPos_i2 > 0:
                            self.enterShort(self.__i2, currentPos_i2)
                            self.__text+=u"卖出"+self.__i2+u"股票"+str(currentPos_i2)+u"股"
                        self.buyUseAllMoney(self.__i1, bars)
                    elif threshold > self.__thresholdStd:  # Buy spread when its value drops below 2 standard deviations.
                        if currentPos_i1 > 0:
                            self.enterShort(self.__i1, currentPos_i1)
                            self.__text += u"卖出" + self.__i1 + u"股票" + str(currentPos_i1) + u"股"
                        self.buyUseAllMoney(self.__i2, bars)
            if self.__text != "":
                self.__textlist.setdefault(bars.getDateTime().date(),self.__text)

class DataCalculator_For_DoubleMA_Strategy():
    def __init__(self,ds,malength_1,malength_2):
        self.__ds = ds
        self.__malength_1=malength_1
        self.__malength_2=malength_2
        self.__ma1=None
        self.__ma2=None
        self.update()
    def getSMA(self,list):
        if list==1:
            return self.__ma1
        if list==2:
            return self.__ma2
    def update(self):
        self.__ma1 = ma.SMA(self.__ds, self.__malength_1)
        self.__ma2 = ma.SMA(self.__ds, self.__malength_2)

class DoubleMA_Strategy(strategy.BacktestingStrategy):
    def __init__(self,feed,brk,instrument,startdate,malength_1,malength_2):
        super(DoubleMA_Strategy, self).__init__(feed, brk)
        self.__DataCalculator = DataCalculator_For_DoubleMA_Strategy(feed[instrument].getPriceDataSeries(),malength_1,malength_2)
        self.__startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
        self.__i = instrument
        self.__position = None

    def onEnterOk(self, position):
        # print position.getEntryOrder().getAction()
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Trade %.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        if bars.getDateTime() >= self.__startdate:
            # If a position was not opened, check if we should enter a long position.
            if self.__DataCalculator.getSMA(2)[-1] is None:
                return

            if self.__position is not None:
                if not self.__position.exitActive() and cross.cross_below(self.__DataCalculator.getSMA(1), self.__DataCalculator.getSMA(2)) > 0:
                    self.__position.exitMarket()
                    # self.info("sell %s" % (bars.getDateTime()))
            if self.__position is None:
                if cross.cross_above(self.__DataCalculator.getSMA(1), self.__DataCalculator.getSMA(2)) > 0:
                    shares = count_shares(self.getBroker().getEquity() * 0.2 / bars[self.__i].getPrice())
                    if shares !=0:
                        self.__position = self.enterLong(self.__i, shares)
        else:
            pass

class DoubleMA_Strategy_Live(strategy.BacktestingStrategy):
    def __init__(self,feed,brk,instrument,builddate,malength_1,malength_2):
        super(DoubleMA_Strategy_Live, self).__init__(feed, brk)
        self.__DataCalculator = DataCalculator_For_DoubleMA_Strategy(feed[instrument].getPriceDataSeries(),malength_1,malength_2)
        self.__builddate=builddate
        self.__i = instrument
        self.__text=''
        self.__textlist={}
        self.__position = None

    def getTextlist(self):
        return self.__textlist

    def onEnterOk(self, position):
        # print position.getEntryOrder().getAction()
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Trade %.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        if bars.getDateTime() > self.__builddate:
            self.__text=''
            # If a position was not opened, check if we should enter a long position.
            if self.__DataCalculator.getSMA(2)[-1] is None:
                return

            if self.__position is not None:
                if not self.__position.exitActive() and cross.cross_below(self.__DataCalculator.getSMA(1), self.__DataCalculator.getSMA(2)) > 0:
                    self.__position.exitMarket()
                    self.__text+=u"卖出"+self.__i+u"以平仓"
                    # self.info("sell %s" % (bars.getDateTime()))
            if self.__position is None:
                if cross.cross_above(self.__DataCalculator.getSMA(1), self.__DataCalculator.getSMA(2)) > 0:
                    shares = count_shares(self.getBroker().getEquity() * 0.2 / bars[self.__i].getPrice())
                    self.__position = self.enterLong(self.__i, shares)
                    self.__text+=u"买入"+self.__i+u"股票"+str(shares)+u"股开仓"

            if self.__text != "":
                self.__textlist.setdefault(bars.getDateTime().date(), self.__text)

class Buy_Everyday_Live(strategy.BacktestingStrategy):
    def __init__(self,feed,brk,instrument,builddate):
        super(Buy_Everyday_Live, self).__init__(feed, brk)
        self.__builddate=builddate
        self.__i = instrument
        self.__text=''
        self.__textlist={}
        self.__position = None

    def getTextlist(self):
        return self.__textlist

    def onEnterOk(self, position):
        # print position.getEntryOrder().getAction()
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("Trade %.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        if bars.getDateTime() > self.__builddate:
            self.__text=''
            shares=100
            # If a position was not opened, check if we should enter a long position.
            self.__position = self.enterLong(self.__i, shares)
            self.__text+=u"买入"+self.__i+u"股票"+str(shares)+u"股开仓"

            if self.__text != "":
                self.__textlist.setdefault(bars.getDateTime().date(), self.__text)

<<<<<<< HEAD
class Stock_Picking_Strategy_Based_Value_By_Steve(strategy.BacktestingStrategy):
    def __init__(self,feed,brk,instrument,malength_1,malength_2):
        super(Stock_Picking_Strategy_Based_Value_By_Steve, self).__init__(feed, brk)
        self.__DataCalculator = ''
        self.__T = 20  #调仓周期
        self.__margin = instrument  #调仓标记 代表距离调仓还有多少天
=======
class DataCalculator_For_Stock_Picking_Strategy_Based_Value_By_Steve_A():
    def __init__(self):
        pass
    def suggest_code_list(self,date, quarter, count):
        list = []
        w.start();
        AllAStock = w.wset("sectorconstituent", "sectorid=a001010100000000;field=wind_code");
        score_list = {}
        gxsyl_all = 0
        gjxjllb_all = 0
        i = 0
        # 计算 股息收益率市场均值 股价现金流量比均值
        for stock in AllAStock.Data[0]:
        # for i in range(0, 5):
        #     stock = AllAStock.Data[0][i]
            data_tmp1 = w.wsd(stock, "dividendyield2,close",
                              date, date, "unit=1;rptType=1;Days=Alldays;Fill=Previous")
            data_tmp2 = w.wsd(stock, "cfps",
                              quarter, date, "currencyType=;Period=Q;Days=Alldays")

            for n in data_tmp1.Data:
                if (str(n[0]) != 'nan' and str(data_tmp2.Data[0][0]) != 'nan'):
                    gxsyl_all += n[0]
                    gjxjllb_all += n[0] / data_tmp2.Data[0][0]
                    i += 1

        gxsyl_avg = gxsyl_all / i
        gjxjllb_avg = gjxjllb_all / i

        # 获取 市净率（算术平均） 市盈率（算术平均） 流动比率（算术平均）
        # 此处时间格式为yyyymmdd
        date_1 = date.replace('-', '')
        data_3 = w.wsee("a001010100000000", "sec_pb_avg_chn,sec_pe_avg_chn,sec_current_avg_chn",
                        "tradeDate=" + date_1 + ";ruleType=11;excludeRule=1;DynamicTime=1;rptDate=20161231")
        sec_pb_avg_chn = data_3.Data[0][0]
        sec_pe_ttm_avg_glb = data_3.Data[1][0]
        sec_current_avg_chn = data_3.Data[2][0]

        # print(AllAStock)
        # for stock in AllAStock.Data[0]:
        for i in range(0, 5):
            stock = AllAStock.Data[0][i]
            score_1 = 0
            score_2 = 0
            score_3 = 0
            score_4 = 0
            score_5 = 0
            score_6 = 0
            score_7 = 0

            # 获取 市净率，市盈率，每股流动资产，股息率，每股现金流量急净额，收盘价，
            data_1 = w.wsd(stock, "pb_lf,pe_lyr,wgsd_bps,dividendyield2,close",
                           date, date, "unit=1;rptType=1;Days=Alldays;Fill=Previous")
            # 获取 长期借贷，流动比率,总资本
            data_2 = w.wsd(stock, "lt_borrow,wgsd_current,cap_stk,cfps",
                           quarter, date, "unit=1;rptType=1;Period=Q;Days=Alldays;Fill=Previous")

            for n in data_1.Data[0]:
                if (str(n) != 'nan'):
                    pb_lf = data_1.Data[0][0]
                    pe_lyr = data_1.Data[1][0]
                    wgsd_bps = data_1.Data[2][0]
                    dividendyield2 = data_1.Data[3][0]
                    close = data_1.Data[4][0]

                    lt_borrow = data_2.Data[0][0]
                    wgsd_current = data_2.Data[1][0]
                    cap_stk = data_2.Data[2][0]
                    cfps = data_2.Data[3][0]

                # 市净率低于全市场平均值 （全市场平均值-市净率）/ 全市场平均值
                if (pb_lf < sec_pb_avg_chn):
                    score_1 = (sec_pb_avg_chn - pb_lf) / sec_pb_avg_chn

                # 以五年平均盈余计算的PE低于全市场平均值 （全市场平均值-PE）/ 全市场平均值
                if (pe_lyr < sec_pe_ttm_avg_glb):
                    score_2 = (sec_pe_ttm_avg_glb - pe_lyr) / sec_pe_ttm_avg_glb

                # 每股流动资产至少是股价的30%
                if ((wgsd_bps / close) >= 0.3):
                    score_3 = (wgsd_bps - close) / wgsd_bps

                # 股息收益率不低于全市场平均值
                if (dividendyield2 > gxsyl_avg):
                    score_4 = (dividendyield2 - gxsyl_avg) / dividendyield2

                # 股价现金流量比低于全市场平均值
                if ((close / cfps) < gjxjllb_avg):
                    score_5 = (gjxjllb_avg - (close / cfps)) / gjxjllb_avg

                # 长期借款占总资本比例低于50% 此处出现离群点
                if ((lt_borrow / cap_stk) < 0.5):
                    score_6 = (cap_stk - lt_borrow) / cap_stk
                #  流动比例高于全市场平均值（无调整）
                if (wgsd_current >= sec_current_avg_chn):
                    score_7 = (wgsd_current - sec_current_avg_chn) / wgsd_current

            #     总分数
            score = score_1 + score_2 + score_3 + score_4 + score_5 + score_6 + score_7
            score_list[stock] = score
        # 将字典转化为元组并从小到大排序
        scorted_list = sorted(zip(score_list.values(), score_list.keys()))

        # for i in (len(scorted_list)-2,len(scorted_list)-1):
        # list.append(scorted_list[i][1])
        print(scorted_list)
        return list

class Stock_Picking_Strategy_Based_Value_By_Steve_A(strategy.BacktestingStrategy):
    def __init__(self,feed,brk,startdate,time_period,T=20):
        super(Stock_Picking_Strategy_Based_Value_By_Steve_A, self).__init__(feed, brk)
        self.__process_bar=ShowProcess(time_period)
        self.__DataCalculator =DataCalculator_For_Stock_Picking_Strategy_Based_Value_By_Steve_A()
        self.__T = T  #调仓周期
        self.__margin = 0  #调仓标记 代表距离调仓还有多少天
        self.__startdate =datetime.datetime.strptime(startdate,"%Y-%m-%d")
>>>>>>> 78c34cb1f3470e97847f449bbb5ace50d08552fa
        self.__position = None
    def onEnterOk(self, position):
        pass

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        self.__process_bar.show_process()
        if bars.getDateTime() >= self.__startdate:
            today=bars.getDateTime().strftime("%Y-%m-%d")
            if self.__margin==0:
                cur_pos=self.getBroker().getPositions().keys()
                # sug_pos=[] #生成推荐列表
                sug_pos=self.__DataCalculator.suggest_code_list(today,get_last_quarter_date(today),20)
                sell_list=list(set(cur_pos)-set(sug_pos))
                buy_list = list(set(sug_pos) - set(cur_pos))
                if sell_list != []:
                    for stock in sell_list:
                        cur_shares = self.getBroker().getShares(stock)
                        self.enterShort(stock,cur_shares)

                if buy_list!=[]:
                    budget=self.getBroker().getCash(False)/len(buy_list)
                    for stock in buy_list:
                        price = bars[stock].getPrice()
                        volume = count_shares(budget / price)
                        if volume != 0:
                            self.enterLongLimit(stock,price,volume)
                self.__margin=self.__T
            else:
                self.__margin=self.__margin-1
        else:
            pass


#
# if __name__=="__main__":
#     w.start()
#     mystr=Strategy_Manager(Strategy.Stock_Picking_Strategy_Based_Value_By_Steve_A,commission=0.001,cash=100000,startdate='2015-01-01',enddate='2015-12-31')
#     mystr.run()
#     dc=DataCalculator_For_Stock_Picking_Strategy_Based_Value_By_Steve_A()
#     suglist= dc.suggest_code_list('2015-02-15','2014-12-31',20)
#     print suglist
