#encoding:utf-8
from pyalgotrade import strategy,bar
from webapp.Library.pyalgotrade_custom import dataFramefeed
import tushare as ts
from datetime import *
def get_k_data_recent(instruement,startdate):
    # 得到日数据（股票instruement,始于startdate,止于今天）
    data = ts.get_k_data(instruement,startdate)
    return data
class Profit_monitoring():
    mylist=[]
    __status__='null'
    def __init__(self,data):
        if (data != []):
            self.__status__='exist'
            for result in data:
                self.mylist.append(
                    {"code": result.code, "position": result.position, "price": result.price, "amount": result.amount,
                     "commission": result.commission, "time": result.time.strftime('%Y-%m-%d')})
    def clear(self):
        self.mylist=[]
    def getfeed(self):
        __codelist__=[]
        __time__=''
        feed = dataFramefeed.Feed(bar.Frequency.DAY)
        for i in self.mylist:
            __time__=i['time']
            if i['code'] not in __codelist__:
                __codelist__.append(i['code'])
        for i in __codelist__:
            idf=get_k_data_recent(i,__time__)
            feed.addBarsFromDataFrame(i,idf )
        return feed
    def start(self):
        if self.__status__=='null':
            return {"result":"empty"}
        else:
            barfeed=self.getfeed()
            myStrategy=Profit_monitoring_strategy(barfeed,self.mylist)
            myStrategy.run()
            date=myStrategy.date
            profit=myStrategy.profit
            cost=myStrategy.cost
            value=myStrategy.value
            return {"date":date,"profit":profit,"cost":cost,"value":value}

class Profit_monitoring_strategy(strategy.BacktestingStrategy):
    date=[]
    profit=[]
    cost=[]
    value=[]
    __handlelist__=[]
    __profit__=0
    __cost__=0
    __order__=0
    __maxorder__=0
    __position__={}
    def __init__(self, feed,mylist):
        super(Profit_monitoring_strategy, self).__init__(feed)
        self.__position = None
        self.__handlelist__=mylist
        self.__maxorder__=len(mylist)
        self.__order__=self.__maxorder__-1
        self.date=[]
        self.cost=[]
        self.profit=[]
        self.value=[]
        self.__position__={}
    def onBars(self, bars):
        # 1.判断日期符合 是否买入卖出
        __value=0
        t=self.__handlelist__[self.__order__]['time']
        d = datetime.strptime(t, '%Y-%m-%d')
        if bars.getDateTime() == d:
            if self.__handlelist__[self.__order__]['position']=='buy':
                # print self.__handlelist__[self.__order__]['amount']
                # print self.__handlelist__[self.__order__]['price']
                # print self.__handlelist__[self.__order__]['commission']
                self.__cost__+=self.__handlelist__[self.__order__]['amount'] * self.__handlelist__[self.__order__]['price'] * (1+self.__handlelist__[self.__order__]['commission'])
                if self.__position__.has_key(self.__handlelist__[self.__order__]['code']):
                    self.__position__[self.__handlelist__[self.__order__]['code']]+=self.__handlelist__[self.__order__]['amount']
                else:
                    self.__position__.setdefault(self.__handlelist__[self.__order__]['code'],self.__handlelist__[self.__order__]['amount'])
            if self.__handlelist__[self.__order__]['position']=='sell':
                self.__cost__ -= self.__handlelist__[self.__order__]['amount'] * self.__handlelist__[self.__order__][
                    'price'] * (1 + self.__handlelist__[self.__order__]['commission'])
                self.__position__[self.__handlelist__[self.__order__]['code']] -= self.__handlelist__[
                    self.__order__]['amount']
            self.__order__ -= 1
        #2、计算持仓价值
        for key in self.__position__:
            bar = bars.getBar(key)
            if bar is not None:
                __value+=bar.getClose()*self.__position__[key]
        self.__profit__ = __value - self.__cost__
        self.profit.append(self.__profit__)
        self.date.append(bars.getDateTime().strftime('%Y-%m-%d'))
        self.cost.append(self.__cost__)
        self.value.append(__value)

            # 日期转换
            # t_str = '2015-4-1'
            # d = datetime.strptime(t_str, '%Y-%m-%d')
            # if bar.getDateTime() == d:

