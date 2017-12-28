#encoding:utf-8
from pyalgotrade import strategy,bar
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
import tushare as ts
import pandas as pd
import os
from datetime import *
def get_k_data_recent(instruement,startdate):
    path='/var/www/wsgi-scripts/webapp/histdata'
    # 得到15分钟数据（股票300336,始于2016-01-01,止于2016-05-24,15分钟数据）
    data = ts.get_k_data(instruement,startdate)
    # 数据存盘
    filepath = os.path.join(path, instruement+'_ts.csv')
    data.to_csv(filepath)
    # 读出数据，DataFrame格式
    df = pd.read_csv(filepath)
    # 从df中选取数据段，改变段名；新段'Adj Close'使用原有段'close'的数据
    df2 = pd.DataFrame({'Date Time': df['date'], 'Open': df['open'],
                        'High': df['high'], 'Close': df['close'],
                        'Low': df['low'], 'Volume': df['volume'],
                        'Adj Close': df['close']})
    # 按照Yahoo格式的要求，调整df2各段的顺序
    dt = df2.pop('Date Time')
    df2.insert(0, 'Date Time', dt)
    o = df2.pop('Open')
    df2.insert(1, 'Open', o)
    h = df2.pop('High')
    df2.insert(2, 'High', h)
    l = df2.pop('Low')
    df2.insert(3, 'Low', l)
    c = df2.pop('Close')
    df2.insert(4, 'Close', c)
    v = df2.pop('Volume')
    df2.insert(5, 'Volume', v)
    # 新格式数据存盘，不保存索引编号
    filepath = os.path.join(path, instruement + '.csv')
    df2.to_csv(filepath, index=False)
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
        feed = GenericBarFeed(bar.Frequency.DAY)
        feed.setDateTimeFormat('%Y-%m-%d')  # 日期读取
        for i in self.mylist:
            __time__=i['time']
            if i['code'] not in __codelist__:
                __codelist__.append(i['code'])
        for i in __codelist__:
            get_k_data_recent(i,__time__)
            feed.addBarsFromCSV(i, os.path.join('/var/www/wsgi-scripts/webapp','histdata',i+'.csv'))
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

