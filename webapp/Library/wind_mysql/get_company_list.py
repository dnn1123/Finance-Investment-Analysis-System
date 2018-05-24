# coding: UTF-8

# 初始化接口#
from WindPy import *
import pandas as pd
import json
from webapp.models import *
import MySQLdb, time, re
import time as Time
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker
import numpy as np
import xlrd,os

# 测试期间所有函数只读取两条股票

def upData_company_list():
    data ={}
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    data = xlrd.open_workbook(os.path.abspath(os.path.dirname(__file__))+'/score.xls')
    # 获取分数表
    table = data.sheet_by_name(u'sheet_score')
    list_stock_code = np.array(table.col_values(0))
    list_score = np.array(table.col_values(8))
    print list_score
    list_score.astype('float64')
    # 取大于得分20%，40%，60%，80%分位数
    quantile_20 =np.percentile(list_score,20)
    quantile_40 = np.percentile(list_score,40)
    quantile_60 = np.percentile(list_score,60)
    quantile_80 = np.percentile(list_score,80)

    for i in range(0,len(list_stock_code)):

        result = stock_grade_l.query.filter_by(trade_code=list_stock_code[i][0:6]).first()
        if result is None:
            continue
        else:
            print i
            position = np.where(list_stock_code == result.trade_code)
            if i<=50:
                result.grade_id='aaa'
            elif i>50 and i<=200:
                result.grade_id='aa'
            elif i>200 and i<=450:
                result.grade_id='a'
            elif i>450 and i<=800:
                result.grade_id='bbb'
            elif i>800 and i<=1250:
                result.grade_id='bb'
            elif i>1250 and i<=1800:
                result.grade_id='b'
            elif i>1800 and i<=2450:
                result.grade_id='ccc'
            elif i>2450 and i<=3200:
                result.grade_id='cc'
            elif i>3200:
                result.grade_id='c'
            db.session.commit()
    return data

