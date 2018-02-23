# coding=utf-8
import numpy as np
import statsmodels.api as sm
from pyalgotrade.dataseries import aligned
from pyalgotrade import strategy,broker, bar
from pyalgotrade.stratanalyzer import returns, sharpe, drawdown, trades
from pyalgotrade.utils import stats
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from enum import Enum, unique
from webapp.Library.pyalgotrade_custom import dataFramefeed,plotter
import tushare as ts

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

@unique
class Strategy(Enum):
    Pair_Strategy_Based_Bank = 0  # 设置sun 的value为  策略id 数据库
    DoubleMA_Strategy=1
    # Sat = 6 # 如果重复会报错 TypeError: Attempted to reuse key: 'Sat'
    # @unique装饰器可以帮助我们检查保证没有重复值

class Strategy_Manager():  # 策略管理器
    def __init__(self, StrategyType, **args):
        self.__strategy_type = StrategyType
        if StrategyType == Strategy.Pair_Strategy_Based_Bank:
            self.__commission = args.get('commission')
            self.__startdate = args.get('startdate')
            self.__enddate = args.get('enddate')
            self.__cash = args.get('cash')
            self.__i1 = args.get('instrument_1')
            self.__i2 = args.get('instrument_2')
            self.__init_Pair_Strategy_Based_Bank()

        if StrategyType==Strategy.DoubleMA_Strategy:
            self.__commission = args.get('commission')
            self.__startdate = args.get('startdate')
            self.__enddate = args.get('enddate')
            self.__cash = args.get('cash')
            self.__i = args.get('instrument')
            self.__init_DoubleMA_Strategy()
    def __init_Pair_Strategy_Based_Bank(self):

        i1_data = ts.get_k_data(self.__i1, self.__startdate, self.__enddate)
        i2_data = ts.get_k_data(self.__i2, self.__startdate, self.__enddate)
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
        self.__strategy_entity = Pair_Strategy_Based_Bank(feed, brk, self.__i1, self.__i2, 50)

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
        i_data = ts.get_k_data(self.__i, self.__startdate, self.__enddate)
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
        self.__strategy_entity = DoubleMA_Strategy(feed, brk, self.__i,5,20)

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

# ds1 gong ds2 nong
# 需要一个策略管理器 负责搭建策略 即生成参数 调用策略 提供暂停 销毁等功能
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
    def __init__(self, feed, brk, instrument1, instrument2, interval):
        super(Pair_Strategy_Based_Bank, self).__init__(feed, brk)
        self.__DataCalculator = DataCalculator_For_Pair_Strategy_Based_Bank(feed[instrument1].getAdjCloseDataSeries(),
                                                                            feed[instrument2].getAdjCloseDataSeries(),
                                                                            interval)
        self.__i1 = instrument1
        self.__i2 = instrument2
        self.__thresholdStd = 0
        self.__position = None

    def buyUseAllMoney(self, instrument, bars):
        cash = self.getBroker().getCash(False)
        price = bars[instrument].getPrice()
        size = int(cash / price)
        if size > 0:
            self.enterLong(instrument, size)

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
    def __init__(self,feed,brk,instrument,malength_1,malength_2):
        super(DoubleMA_Strategy, self).__init__(feed, brk)
        self.__DataCalculator = DataCalculator_For_DoubleMA_Strategy(feed[instrument].getPriceDataSeries(),malength_1,malength_2)
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
        # If a position was not opened, check if we should enter a long position.
        if self.__DataCalculator.getSMA(2)[-1] is None:
            return

        if self.__position is not None:
            if not self.__position.exitActive() and cross.cross_below(self.__DataCalculator.getSMA(1), self.__DataCalculator.getSMA(2)) > 0:
                self.__position.exitMarket()
                # self.info("sell %s" % (bars.getDateTime()))
        if self.__position is None:
            if cross.cross_above(self.__DataCalculator.getSMA(1), self.__DataCalculator.getSMA(2)) > 0:
                shares = int(self.getBroker().getEquity() * 0.2 / bars[self.__i].getPrice())
                self.__position = self.enterLong(self.__i, shares)

