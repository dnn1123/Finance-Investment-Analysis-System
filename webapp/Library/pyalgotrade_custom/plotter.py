#encoding:utf-8

from pyalgotrade import broker
from backtestOrder import backtestOrder as Order

class StrategyPlotter(object):
    """Class responsible for plotting a strategy execution.

    :param strat: The strategy to plot.
    :type strat: :class:`pyalgotrade.strategy.BaseStrategy`.
    """

    def __init__(self, strat):
        self.__dateTimes = []
        self.__tradehistory=[]
        self.__portfolio=[]
        self.__startdate=strat.getStartdate()
        strat.getBarsProcessedEvent().subscribe(self.__onBarsProcessed)
        strat.getBroker().getOrderUpdatedEvent().subscribe(self.__onOrderEvent)
    def getTradehistory(self):
        self.__tradehistory.reverse()
        return self.__tradehistory
    def getPortfolio(self):
        point=None
        for i in self.__dateTimes:
            if i>=self.__startdate:
                point=i
                break
        num=self.__dateTimes.index(point)
        return {"date":self.__dateTimes[num:],"data":self.__portfolio[num:]}
    def __onBarsProcessed(self, strat, bars):
        dateTime = bars.getDateTime()
        self.__dateTimes.append(dateTime)
        self.__portfolio.append(strat.getBroker().getEquity())
        # 可以返回市值变化
    def __onOrderEvent(self, broker_, orderEvent):
        order = orderEvent.getOrder()
        if orderEvent.getEventType() in (broker.OrderEvent.Type.PARTIALLY_FILLED,broker.OrderEvent.Type.FILLED):
            code=order.getInstrument()
            action = order.getAction()
            execInfo = orderEvent.getEventInfo()
            if action in [broker.Order.Action.BUY, broker.Order.Action.BUY_TO_COVER]:
                historder = Order(code,'buy',execInfo.getPrice(),execInfo.getQuantity(),execInfo.getCommission(),execInfo.getDateTime())
                self.__tradehistory.append(historder)
            elif action in [broker.Order.Action.SELL, broker.Order.Action.SELL_SHORT]:
                historder = Order(code, 'sell', execInfo.getPrice(), execInfo.getQuantity(), execInfo.getCommission(),
                                  execInfo.getDateTime())
                self.__tradehistory.append(historder)
