#encoding:utf-8
import requests
import pandas as pd
class Wind_Data:
    """
    用途：为了方便客户使用，本类用来把api返回来的C语言数据转换成python能认的数据，从而为用户后面转换成numpy提供方便
         本类包含.ErrorCode 即命令错误代码，0表示错误；
              对于数据接口还有：  .Codes 命令返回的代码； .Fields命令返回的指标；.Times命令返回的时间；.Data命令返回的数据
              对于交易接口还有：  .Fields命令返回的指标；.Data命令返回的数据

    """

    def __init__(self):
        self.ErrorCode = 0
        self.StateCode = 0
        self.RequestID = 0
        self.Codes = list()  # list( string)
        self.Fields = list()  # list( string)
        self.Times = list()  # list( time)
        self.Data = list()  # list( list1,list2,list3,list4)
        self.asDate = False
        self.datatype = 0;  # 0-->DataAPI output, 1-->tradeAPI output
        pass

    def clear(self):
        self.ErrorCode = 0
        self.StateCode = 0
        self.RequestID = 0
        self.Codes = list()  # list( string)
        self.Fields = list()  # list( string)
        self.Times = list()  # list( time)
        self.Data = list()  # list( list1,list2,list3,list4)

    def setErrMsg(self, errid, msg):
        self.clear();
        self.ErrorCode = errid;
        self.Data = [msg];

    def setData(self,indata):
        self.clear()
        self.ErrorCode = indata['ErrorCode']
        self.StateCode = indata['StateCode']
        self.RequestID = indata['RequestID']
        self.Codes = indata['Codes']
        self.Fields = indata['Fields']
        self.Times = indata['Times']
        self.Data = indata['Data']
        self.asDate = indata['asDate']
        self.datatype = indata['datatype']
def Json_to_WindData(data):
    wd=Wind_Data()
    wd.setData(data)
    return wd

def Json_to_DataFrame(data):
    df=pd.DataFrame(data['Data'],columns=data['Times'],index=data['Fields'])
    df = df.T
    df['date'] = data['Times']
    for i in data['Times']:
        print i
    df.rename(columns={'OPEN': 'open', 'HIGH': 'high', 'LOW': 'low', 'CLOSE': 'close', 'VOLUME': 'volume'}, inplace=True)
    return df

class WindData(object):
    def __init__(self,url,port):
        if isinstance(port, str):
            self.__port = port
        elif isinstance(port, int):
            self.__port = str(port)
        self.__url=url
        self.__server_address='http://'+self.__url+':'+self.__port
        self.__timeout= 3.05
    def set_timeout(self,var):
        if isinstance(var, float):
            self.__timeout = var

    def wsd(self,*args):
        url=self.__server_address+'/wind_data/wsd'
        payload={"params":args}
        r = requests.get(url,params=payload,timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data=r.json()
            return Json_to_WindData(data)
        else:
            r.raise_for_status()

    def wsd_df(self,*args):
        url=self.__server_address+'/wind_data/wsd'
        payload={"params":args}
        r = requests.get(url,params=payload,timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data=r.json()
            return Json_to_DataFrame(data)
        else:
            r.raise_for_status()

    def wss(self, *args):
        url = self.__server_address + '/wind_data/wss'
        payload = {"params": args}
        r = requests.get(url, params=payload, timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data = r.json()
            return Json_to_WindData(data)
        else:
            r.raise_for_status()

    def wst(self, *args):
        url = self.__server_address + '/wind_data/wst'
        payload = {"params": args}
        r = requests.get(url, params=payload, timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data = r.json()
            return Json_to_WindData(data)
        else:
            r.raise_for_status()

    def wsi(self, *args):
        url = self.__server_address + '/wind_data/wsi'
        payload = {"params": args}
        r = requests.get(url, params=payload, timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data = r.json()
            return Json_to_WindData(data)
        else:
            r.raise_for_status()

    #回调函数 处理订阅 待解决
    def wsq(self, *args):
        url = self.__server_address + '/wind_data/wsq'
        payload = {"params": args}
        r = requests.get(url, params=payload, timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data = r.json()
            return Json_to_WindData(data)
        else:
            r.raise_for_status()

    def wsee(self,*args):
        url=self.__server_address+'/wind_data/wsee'
        payload={"params":args}
        r = requests.get(url,params=payload,timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data=r.json()
            return Json_to_WindData(data)
        else:
            r.raise_for_status()

    def wset(self, *args):
        url = self.__server_address + '/wind_data/wset'
        payload = {"params": args}
        r = requests.get(url, params=payload, timeout=self.__timeout)
        if r.status_code == requests.codes.ok:
            data = r.json()
            return Json_to_WindData(data)
        else:
            r.raise_for_status()

    #部分数据函数 交易模块暂时先不写了 以后用到再说 涉及到回调问题

