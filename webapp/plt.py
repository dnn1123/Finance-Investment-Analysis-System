#coding=utf-8
from webapp.models import *
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties # 解决中文显示的问题
font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=15)

# 连接数据库并查询结果集
db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
Session = sessionmaker(bind=db_engine)
session = Session()
rs = session.query(finance_basics).filter(finance_basics.trade_code == '000895').order_by(
    finance_basics.the_year.asc()).all()
# 获得指标的最大值
rs_max = session.query(func.max(finance_basics.tot_oper_rev).label("mx_tot_oper_rev")).filter(finance_basics.trade_code=='000895').all()

# 这是x轴数据集
x = []
for i in range(len(rs)):
    if rs[i].tot_oper_rev == None:
        x.append(0)
    else:
        x.append(round(rs[i].tot_oper_rev/100000000,2))

x_net_profit_rate = []
for i in range(len(rs)):
    if rs[i].tot_oper_rev == None:
        x_net_profit_rate.append(0)
    else:
        x_net_profit_rate.append(round(((rs[i].net_profit_is / rs[i].tot_oper_rev) * 100), 2))

# 这是x轴标签，顶部要空出一行
xlabels = []
for i in range(len(rs)):
    xlabels.append(rs[i].the_year[:4])

# 设置双y轴
fig, ax1 = plt.subplots()
ax1.set_xticklabels(rotation=45)
ax1.bar(range(len(x)),x,tick_label=xlabels,color='#BEBEBE',yerr=True) #color显示rgb颜色
ax2 = ax1.twinx()
ax2.plot(x_net_profit_rate)

# x轴年份旋转后显示；这行注释不能写在上一行；
# plt.xticks(rotation=50)

plt.title(u'营业总收入', fontproperties=font_set) # 可以动态显示
# 设置y轴上限,为所有年中最大的指标
# plt.ylim(0,max(x)*1.1) # 对x列表直接使用max()函数
# plt.legend()
# plt.bar(range(len(x)),x,tick_label=xlabels,color='#BEBEBE',yerr=True) #color显示rgb颜色
plt.xlabel(u'年份', fontproperties=font_set) # 添加fontproperties=font_set才能显示中文
# plt.ylabel(u'营业总收入（单位：亿元）', fontproperties=font_set)

fig.tight_layout()
plt.show()