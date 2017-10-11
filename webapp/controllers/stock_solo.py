#coding=utf-8
from flask import Blueprint,redirect,render_template,url_for,request
from os import path
from webapp.models import *
from webapp.forms import CodeForm,graph_Form
from flask_login import login_required,current_user
from webapp.extensions import finance_analyst_permission # 这个就是经济师权限
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import MySQLdb,time,re #re用于判断是否含中文
import numpy as np
import matplotlib.pyplot as plt # 画图用
from matplotlib.font_manager import FontProperties # 解决画图时的中文显示的问题
font_set = FontProperties(fname=r"c:\windows\fonts\msyh.ttf", size=12) #画图设置微软雅黑字体
import matplotlib.patheffects as path_effects # 显示线条的阴影
import restfulapi

#用于判断是否含中文
zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
stocksolo_blueprint = Blueprint(
    'stock_solo',
    __name__,
    template_folder=path.join(path.pardir,'templates','stock_solo'),
    url_prefix="/stock_solo"
)
@stocksolo_blueprint.route('/',methods=('GET','POST'))
@stocksolo_blueprint.route('/<string:data>',methods=('GET','POST'))
@login_required
# @finance_analyst_permission.require(http_exception=403)
# 自动补全代码和数字、中文混输功能
def basic(data='000895'):
    data = data
    form = CodeForm()
    if form.validate_on_submit():
        data = form.code.data
        # match = zhPattern.search(data)
        return redirect(url_for('stock_solo.basic', current_user=current_user, data=data))
    match = zhPattern.search(data)
    if match:
        stock = stock_basics.query.filter_by(sec_name=data).first_or_404()
    else:
        stock = stock_basics.query.filter_by(trade_code=data).first_or_404()

    # rs = stock_basics.query.with_entities(stock_basics.trade_code,stock_basics.sec_name)
    # length = stock_basics.query.count()
    # list_len = range(length)
    return render_template("stock_solo/stock_solo_basic.html",current_user=current_user, form=form,stock=stock)

@stocksolo_blueprint.route('/finance_data',methods=('GET','POST'))
@stocksolo_blueprint.route('/finance_data/<string:data>',methods=('GET','POST'))
# @stocksolo_blueprint.route('/<string:data>',methods=('GET','POST'))
@login_required
# @finance_analyst_permission.require(http_exception=403)

def finance_data(data='000895'):
    data=data
    form = CodeForm()
    if form.validate_on_submit():
        data = form.code.data
        # match = zhPattern.search(data)
        return redirect(url_for('stock_solo.finance_data', current_user=current_user, data=data))
    match = zhPattern.search(data)
    if match:
        stock = stock_basics.query.filter_by(sec_name=data).first_or_404()
    else:
        stock = stock_basics.query.filter_by(trade_code=data).first_or_404()

    # form = CodeForm()
    # if form.validate_on_submit():
    #    trade_code = form.code.data
    #    return redirect(url_for('stock_solo.finance_data',current_user=current_user,trade_code=trade_code))

    # db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    # Session = sessionmaker(bind=db_engine)
    # session = Session()
    # stock_list = session.query(stock_basics.trade_code,stock_basics.trade_code).all()

# connect database
    stock_list = []
    stock_source = stock_basics.query.all()
    for x in stock_source:
        stock_list.append(x.trade_code) # 这种写法没有括号

    year_list = []
    yearnow = time.strftime('%Y', time.localtime(time.time()))
    year_now = yearnow + '1231'
    year_now = int(year_now)-10000
    n = 26
    while n > 0:
        year_list.append(year_now)
        year_now = int(year_now) - 10000
        n = n - 1

    year_list_1 = year_list[:-1]

    results = []
    for t in year_list:
        result = finance_basics.query.filter_by(trade_code=data,the_year=(t)).first_or_404()
        results.append(result)

    ratio_RG = []
    for i in year_list_1:
        ratio_RG1 = finance_basics.query.filter_by(trade_code=data,the_year=(i)).first_or_404()
        ratio_RG2 = finance_basics.query.filter_by(trade_code=data,the_year=(i-10000)).first_or_404()
        if ratio_RG1.tot_oper_rev == None or ratio_RG2.tot_oper_rev == None or ratio_RG2.tot_oper_rev == 0 :
            ratio_RG.append(None) # 上边为什么有括号？？？
        else:
            ratio_test_RG = ratio_RG1.tot_oper_rev/ratio_RG2.tot_oper_rev
            ratio_RG.append(ratio_test_RG)

    ratio_CG = []
    for i in year_list_1:
        ratio_CG1 = finance_basics.query.filter_by(trade_code=data, the_year=(i)).first_or_404()
        ratio_CG2 = finance_basics.query.filter_by(trade_code=data, the_year=(i - 10000)).first_or_404()
        if ratio_CG1.wgsd_net_inc == None or ratio_CG2.wgsd_net_inc == None or ratio_CG2.wgsd_net_inc == 0:
            ratio_CG.append(None)
        else:
            ratio_test_CG = ratio_CG1.wgsd_net_inc / ratio_CG2.wgsd_net_inc
            ratio_CG.append(ratio_test_CG)

# 自动补全代码
    conn = MySQLdb.connect(user="root", passwd="0000", db="test", charset="utf8")
    cursor = conn.cursor()
    cursor.execute('select distinct trade_code,sec_name from finance_basics')
    value = cursor.fetchall()
    data_len = range(len(value))

    return render_template("stock_solo/stock_solo_finance_data.html",stock_list=stock_list, value=value, data_len=data_len, current_user=current_user,form=form, results=results, ratio_RG=ratio_RG, ratio_CG=ratio_CG)

@stocksolo_blueprint.route('/invest_value',methods=('GET','POST'))
@stocksolo_blueprint.route('/invest_value/<string:data>',methods=('GET','POST'))
# @login_required
# @finance_analyst_permission.require(http_exception=403)

def invest_value(data='000895'):
    data = data
    form = CodeForm()
    if form.validate_on_submit():
        data = form.code.data
        # match = zhPattern.search(data)
        return redirect(url_for('stock_solo.invest_value', current_user=current_user, data=data))
    match = zhPattern.search(data)
    if match:
        stock = stock_basics.query.filter_by(sec_name=data).first_or_404()
    else:
        stock = stock_basics.query.filter_by(trade_code=data).first_or_404()
    return render_template("stock_solo/finance_data.html",form=form)
# # 设定年份数据
#     year_list = []
#     yearnow = time.strftime('%Y', time.localtime(time.time()))
#     year_now = yearnow + '1231'
#     year_now = int(year_now)-10000
#     n = 26
#     while n > 0:
#         year_list.append(year_now)
#         year_now = int(year_now) - 10000
#         n = n - 1
#
#     results = []
#     for t in year_list:
#         result = finance_basics.query.filter_by(trade_code=data,the_year=(t)).first_or_404()
#         results.append(result)
#
#     invest_results = []
#     for x in year_list:
#         invest_result = invest_values.query.filter_by(trade_code=data,the_year=(x)).first_or_404()
#         # 有_or_404()就好使了？！
#         invest_results.append(invest_result)
#
#     earnings_per_share = []  # 每股收益
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (invest_result.total_shares == None or invest_result.total_shares == 0) or (result.wgsd_net_inc == None):
#             earnings_per_share.append(None)
#         else:
#             result_ready = result.wgsd_net_inc / invest_result.total_shares
#             earnings_per_share.append(result_ready)
#
#     payment_proportion = []  # 支付比例
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (invest_result.total_shares == None) or (result.wgsd_net_inc == None or result.wgsd_net_inc == 0) or (
#             invest_result.div_cashandstock == None):
#             payment_proportion.append(None)
#         else:
#             result_ready = (invest_result.total_shares * invest_result.div_cashandstock) / result.wgsd_net_inc
#             payment_proportion.append(result_ready)
#
#     net_assets_per_share = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.wgsd_net_inc == None) or (invest_result.total_shares == None or invest_result.total_shares == 0):
#             net_assets_per_share.append(None)
#         else:
#             insert = result.wgsd_com_eq / invest_result.total_shares
#             net_assets_per_share.append(insert)
#
#     cash_per_share = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.monetary_cap == None) or (invest_result.total_shares == None or invest_result.total_shares == 0):
#             cash_per_share.append(None)
#         else:
#             insert = result.monetary_cap / invest_result.total_shares
#             cash_per_share.append(insert)
#
#     cash_dividend_per_share = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.monetary_cap == None) or (invest_result.total_shares == None or invest_result.total_shares == 0):
#             cash_dividend_per_share.append(None)
#         else:
#             insert = result.monetary_cap / invest_result.total_shares
#             cash_dividend_per_share.append(insert)
#
#     equal_market_rate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.wgsd_net_inc == None) or (result.wgsd_com_eq == None or result.wgsd_com_eq == 0) or (
#             ((1 - result.wgsd_net_inc / result.wgsd_com_eq) ** 5) == 0):
#             equal_market_rate.append(None)
#         else:
#             insert = 1 / ((1 - result.wgsd_net_inc / result.wgsd_com_eq) ** 5)
#             equal_market_rate.append(insert)
#
#     equal_earning_rate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.wgsd_net_inc == None or result.wgsd_net_inc == 0) or (
#                 result.wgsd_com_eq == None or result.wgsd_com_eq == 0):
#             equal_earning_rate.append(None)
#         else:
#             insert = (1 / ((1 - result.wgsd_net_inc / result.wgsd_com_eq) ** 5)) / (
#             result.wgsd_net_inc / result.wgsd_com_eq)
#             equal_earning_rate.append(insert)
#
#     com_value_evaluate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.wgsd_net_inc == None or result.wgsd_net_inc == 0) or (
#                 result.wgsd_com_eq == None or result.wgsd_com_eq == 0):
#             com_value_evaluate.append(None)
#         else:
#             insert = result.wgsd_net_inc * (
#             (1 / ((1 - result.wgsd_net_inc / result.wgsd_com_eq) ** 5)) / (result.wgsd_net_inc / result.wgsd_com_eq))
#             com_value_evaluate.append(insert)
#
#     per_com_value_evaluate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.wgsd_net_inc == None or result.wgsd_net_inc == 0) or (
#                 result.wgsd_com_eq == None or result.wgsd_com_eq == 0):
#             per_com_value_evaluate.append(None)
#         else:
#             insert = (result.wgsd_net_inc * ((1 / ((1 - result.wgsd_net_inc / result.wgsd_com_eq) ** 5)) / (
#             result.wgsd_net_inc / result.wgsd_com_eq))) / invest_result.total_shares
#             per_com_value_evaluate.append(insert)
#
#     earning_rate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.wgsd_net_inc == None or result.wgsd_net_inc == 0) or (invest_result.ev == None):
#             earning_rate.append(None)
#         else:
#             insert = invest_result.ev / result.wgsd_net_inc
#             earning_rate.append(insert)
#
#     net_rate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.wgsd_com_eq == None or result.wgsd_com_eq == 0) or (invest_result.ev == None):
#             net_rate.append(None)
#         else:
#             insert = invest_result.ev / result.wgsd_com_eq
#             net_rate.append(insert)
#
#     sale_rate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.tot_oper_rev == None or result.tot_oper_rev == 0) or (invest_result.ev == None):
#             sale_rate.append(None)
#         else:
#             insert = invest_result.ev / result.tot_oper_rev
#             sale_rate.append(insert)
#
#     cash_rate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.operatecashflow_ttm2 == None or result.operatecashflow_ttm2 == 0) or (invest_result.ev == None):
#             cash_rate.append(None)
#         else:
#             insert = invest_result.ev / result.operatecashflow_ttm2
#             cash_rate.append(insert)
#
#     cash_yield_evaluate = []
#     for x in year_list:
#         result = finance_basics.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         invest_result = invest_values.query.filter_by(trade_code=data, the_year=(x)).first_or_404()
#         if (result.operatecashflow_ttm2 == None) or (invest_result.ev == None or invest_result.ev == 0) or (
#             result.investcashflow_ttm2 == None):
#             cash_yield_evaluate.append(None)
#         else:
#             insert = (result.operatecashflow_ttm2 + result.investcashflow_ttm2) / invest_result.ev
#             cash_yield_evaluate.append(insert)
#
# # 自动补全代码
#     conn = MySQLdb.connect(user="root", passwd="0000", db="test", charset="utf8")
#     cursor = conn.cursor()
#     cursor.execute('select distinct trade_code,sec_name from finance_basics')
#     value = cursor.fetchall()
#     data_len = range(len(value))
#
#     return render_template("stock_solo/stock_solo_invest_value.html", value=value, data_len=data_len,current_user=current_user, form=form,results=results,invest_results=invest_results,earnings_per_share=earnings_per_share, net_assets_per_share=net_assets_per_share,cash_per_share=cash_per_share, equal_market_rate=equal_market_rate,equal_earning_rate=equal_earning_rate, com_value_evaluate=com_value_evaluate,per_com_value_evaluate=per_com_value_evaluate, earning_rate=earning_rate,net_rate=net_rate, sale_rate=sale_rate, cash_rate=cash_rate,cash_yield_evaluate=cash_yield_evaluate, payment_proportion=payment_proportion)

# a = db.session.query(finance_basics.the_year).all() 获取所有年份
# 正在维护的功能
@stocksolo_blueprint.route('/maintanance',methods=('GET','POST'))
def maintanance():
    return render_template("maintanance.html")

# ----图表分析----
@stocksolo_blueprint.route('/graph',methods=('GET','POST'))
@stocksolo_blueprint.route('/graph/<string:graph_id>/<int:year_id>',methods=('GET','POST'))
@login_required
def graph(search_img='1',search_year=10):
    graph_form = graph_Form()
    trade_code = '000895'

    if request.method == 'POST': # 如果提交表单则获取新的graph_id
        search_img = request.form.get('graph_id') # 获取用户要查询的 图片代码
        temp = request.form.get('year_id')  # 获取用户要查询的 时间段
        search_year = int(temp)
    else :
        search_img = search_img
        search_year = search_year

    # 以下为数据集，连接数据库并查询结果集
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    rs_finan = session.query(finance_basics).filter(finance_basics.trade_code == '000895').order_by(finance_basics.the_year.desc()).all()
    rs_inves = session.query(invest_values).filter(invest_values.trade_code == '000895').order_by(invest_values.the_year.desc()).all()
    rs = finance_basics_add.query.filter(finance_basics_add.trade_code == '000895').order_by(finance_basics_add.the_year.desc()).all()

    # 设置x轴（通用）
    year_list = []
    yearnow = time.strftime('%Y', time.localtime(time.time()))
    year_end = int(yearnow) - 1
    n = search_year # 根据search_year来设置x轴
    while n > 0:
        year_list.append(year_end)
        year_end = year_end - 1
        n = n - 1
    year_list.reverse()
    # 以下共 12种图表
    if search_img == '1':
        n = search_year # 年份数据
        a=[] # 营业总收入
        for i in range(n):
            if rs_finan[i].tot_oper_rev == None:
                a.append(0)
            else:
                a.append((rs_finan[i].tot_oper_rev/100000000))
        a.reverse()

        b = []
        for i in range(n):
            if rs[i].net_profit_rate == None or rs[i].net_profit_rate == 0 :
                b.append(0)
            else:
                b.append(round(rs[i].net_profit_rate*100,2))
        b.reverse()

        # b=[] # 净利润率
        # for i in range(n):
        #     if rs_finan[i].tot_oper_rev == None:
        #         b.append(0)
        #     else:
        #         b.append(round(((rs_finan[i].net_profit_is / rs_finan[i].tot_oper_rev) * 100), 2))
        #
        # b.reverse()

        # 设置双y轴
        fig, ax1 = plt.subplots()
        p1 = ax1.bar(range(len(a)), a, width=0.3, ls='--', lw='3', color='#A6A6A6')  # color显示rgb颜色
        # !*! 这样才能显示x轴
        ax1.set_xticks(range(len(year_list)))
        ax1.set_xticklabels(year_list)  # 可以旋转

        ax2 = ax1.twinx()
        p2 = ax2.plot(b, '-*', linewidth=2, color='#C00000',
                      path_effects=[path_effects.SimpleLineShadow(), path_effects.Normal()])
        # ax2.set_ylim(0, max(b) * 1.2)  # 这样就可以使另一个y轴从0开始，乘1.1设置顶部留空

        plt.title(u'营业总收入与净利润率', fontproperties=font_set)  # 可以动态显示
        # ax1.set_xtitle('Sharing Y axis') 另一种方法

        ax1.tick_params(direction='out', length=2, width=2)
        ax2.tick_params(direction='out', length=2, width=2, colors='#CD0000')
        ax2.yaxis.grid(linestyle='--')  # 只显示横线
        plt.legend((p1[0], p2[0]), (u'营业总收入（单位：亿元）', u'净利润率（单位：%）'), prop=font_set,loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=2)
        fig.set_size_inches(12,6)
        # 保存文件格式：证券代码-图表名字-年份year.svg
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/'+trade_code+'-revenue_and_netprofitrate-'+str(n)+'year.svg')

    if search_img == '2': # 这个模块写的不优
        n = search_year  # 年份数据
        year_list=year_list
        # 数据集
        ratio_RG = [] # 收入增长率
        for i in year_list:
            ratio_RG1 = finance_basics.query.filter(finance_basics.trade_code=="000895").filter(finance_basics.the_year == (str(i)+'1231')).first_or_404()
            ratio_RG2 = finance_basics.query.filter(finance_basics.trade_code=="000895").filter(finance_basics.the_year==(str(i-1)+'1231')).first_or_404()
            if ratio_RG1.tot_oper_rev == None or ratio_RG2.tot_oper_rev == None or ratio_RG2.tot_oper_rev == 0:
                ratio_RG.append(0)
            else:
                ratio_temp_RG = ratio_RG1.tot_oper_rev / ratio_RG2.tot_oper_rev
                ratio_RG.append((ratio_temp_RG-1)*100)

        ratio_CG = [] # 利润增长率
        for i in year_list:
            ratio_CG1 = finance_basics.query.filter(finance_basics.trade_code=="000895").filter(finance_basics.the_year==(str(i)+'1231')).first_or_404()
            ratio_CG2 = finance_basics.query.filter(finance_basics.trade_code=="000895").filter(finance_basics.the_year==(str(i-1)+'1231')).first_or_404()
            if ratio_CG1.wgsd_net_inc == None or ratio_CG2.wgsd_net_inc == None or ratio_CG2.wgsd_net_inc == 0:
                ratio_CG.append(0)
            else:
                ratio_temp_CG = ratio_CG1.wgsd_net_inc / ratio_CG2.wgsd_net_inc
                ratio_CG.append((ratio_temp_CG-1)*100)

        y1 = ratio_RG[:n]
        y2 = ratio_CG[:n]
        ind = np.arange(n)  # the x locations for the groups
        width = 0.2  # the width of the bars

        fig, ax = plt.subplots()

        rects1 = ax.bar(ind, y1, width, color='#C00000')
        rects2 = ax.bar(ind + width + 0.05, y2, width, color='#A6A6A6')

        ax.set_title(u'收入增长率 与 利润增长率', fontproperties=font_set)
        ax.set_xticks(ind + (width + 0.05) / 2)
        ax.set_xticklabels(year_list)  # 可以旋转

        ax.yaxis.grid(linestyle='--')  # 只显示横线
        ax.legend((rects1[0], rects2[0]), (u'收入增长率（单位：%）', u'利润增长率（单位：%）'), prop=font_set, loc='upper center',
                  bbox_to_anchor=(0.5, -0.05), ncol=2)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-income_profit_rate-' + str(n) + 'year.svg')

    if search_img == '3':  # 这个模块写的不优
        n = search_year # 年份数据
        year_list = year_list
        # rs = finance_basics_add.query.filter(finance_basics_add.trade_code=='000895').order_by(finance_basics_add.the_year.desc()).all()
        # rs = rs_all[:n]
        a = []
        for i in range(n):
            if rs[i].net_assets == None:
                a.append(0)
            else:
                a.append(round(rs[i].net_assets/100000000,2))
        a.reverse()
        b = []
        for i in range(n):
            if rs[i].tot_liab == None:
                b.append(0)
            else:
                b.append(round(rs[i].tot_liab/100000000,2))
        b.reverse()
        c = []
        for i in range(n):
            if rs[i].equ_multi == None:
                c.append(0)
            else:
                c.append(rs[i].equ_multi)
        c.reverse()
        fig, ax1 = plt.subplots()

        x = np.arange(n)
        ax2 = ax1.twinx()
        p1 = ax1.bar(x, a, width=0.4, color='#C00000')
        p2 = ax1.bar(x, b, bottom=a, width=0.4, color='#0070C0')
        p3 = ax2.plot(c, '-*', linewidth=3, color='#7F7F7F',
                      path_effects=[path_effects.SimpleLineShadow(), path_effects.Normal()])
        ax1.set_title(u'资本结构与权益乘数', fontproperties=font_set)
        ax1.set_xticks(x)
        ax1.set_xticklabels(year_list)  # 可以旋转
        ax1.yaxis.grid(linestyle='--')  # 只显示横线
        # ax2.set_ylim(min(c),max(c))  # 这样就可以使另一个y轴从0开始；设置顶部留空

        plt.legend((p1[0], p2[0], p3[0]), (u'净资产', u'负债合计', u'权益乘数'), prop=font_set, loc='upper center',bbox_to_anchor=(0.5, -0.05), ncol=3)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-capital_struc_and_equ_multi-' + str(n) + 'year.svg')

    if search_img == '4':
        n = search_year # 年份数据

        a = []
        for i in range(n):
            if rs_finan[i].wgsd_com_eq == None:
                a.append(0)
            else:
                a.append(round(rs_finan[i].wgsd_com_eq/100000000))
        a.reverse()

        b = []
        for x in range(n):
            # result = finance_basics.query.filter_by(trade_code=trade_code, the_year=(x)).first_or_404()
            if (rs_finan[x].wgsd_net_inc == None or rs_finan[x].wgsd_net_inc == 0) or (
                            rs_finan[x].wgsd_com_eq == None or rs_finan[x].wgsd_com_eq == 0):
                b.append(0)
            else:
                insert = (rs_finan[x].wgsd_net_inc * (
                    (1 / ((1 - rs_finan[x].wgsd_net_inc / rs_finan[x].wgsd_com_eq) ** 5)) / (
                        rs_finan[x].wgsd_net_inc / rs_finan[x].wgsd_com_eq)))
                b.append(round(insert/100000000))
        b.reverse()

        c = [] # 净资产收益率
        for i in range(n):
            if rs_finan[i].wgsd_com_eq == None or rs_finan[i].wgsd_net_inc == None :
                c.append(0)
            else:
                c.append(round(((rs_finan[i].wgsd_net_inc/rs_finan[i].wgsd_com_eq)*100),2))
        c.reverse()

        fig, ax1 = plt.subplots()

        x = np.arange(n)
        ax2 = ax1.twinx()
        width = 0.2
        p1 = ax1.bar(x, a, width=width, color='#C00000')
        p2 = ax1.bar(x + width + 0.05, b, width=width, color='#A6A6A6')
        p3 = ax2.plot(c, '-*', linewidth=2.5, color='#C00000',
                      path_effects=[path_effects.SimpleLineShadow(), path_effects.Normal()])

        ax1.set_title(u'净资产收益率与公司价值估计', fontproperties=font_set)
        ax1.set_xticks(x + (width + 0.05) / 2)
        ax1.set_xticklabels(year_list)  # 可以旋转

        ax1.yaxis.grid(linestyle='--')  # 只显示横线
        # ax2.set_ylim(0, max(c) * 1.1)  # 这样就可以使另一个y轴从0开始；乘1.1设置顶部留空

        plt.legend((p1[0], p2[0], p3[0]), (u'归属股东权益（单位：亿元）', u'公司价值（单位：亿元）', u'净资产收益率（股东）'), prop=font_set, loc='upper center',
                   bbox_to_anchor=(0.5, -0.05), ncol=3)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-roe_tot_and_ev-' + str(n) + 'year.svg')

    if search_img == '5':
        n = search_year # 年份数据
        # rs = session.query(finance_basics_add).filter(finance_basics_add.trade_code == '000895').order_by(finance_basics_add.the_year.desc()).all()
        a = [] # 均衡市净率
        for i in range(n):
            if rs[i].equ_pb == None:
                a.append(0)
            else:
                a.append(rs[i].equ_pb)
        a.reverse()
        b = [] # 均衡市盈率
        for i in range(n):
            if rs[i].equ_pe == None:
                b.append(0)
            else:
                b.append(rs[i].equ_pe)
        b.reverse()
        # 原方法：
        # a = []
        # for x in range(n):
        #     if (rs_finan[x].wgsd_net_inc == None) or (rs_finan[x].wgsd_com_eq == None or rs_finan[x].wgsd_com_eq == 0) or (
        #                 ((1 - rs_finan[x].wgsd_net_inc / rs_finan[x].wgsd_com_eq) ** 5) == 0):
        #         a.append(0)
        #     else:
        #         insert = 1 / ((1 - rs_finan[x].wgsd_net_inc / rs_finan[x].wgsd_com_eq) ** 5)
        #         a.append(round(insert,2))
        # a.reverse()
        #
        # b = []
        # for x in range(n):
        #     if (rs_finan[x].wgsd_net_inc == None or rs_finan[x].wgsd_net_inc == 0) or (
        #                     rs_finan[x].wgsd_com_eq == None or rs_finan[x].wgsd_com_eq == 0):
        #         b.append(0)
        #     else:
        #         insert = (1 / ((1 - rs_finan[x].wgsd_net_inc / rs_finan[x].wgsd_com_eq) ** 5)) / (
        #             rs_finan[x].wgsd_net_inc / rs_finan[x].wgsd_com_eq)
        #         b.append(round(insert,2))
        # b.reverse()

        # 设置双y轴
        fig, ax1 = plt.subplots()
        p1 = ax1.bar(range(len(b)), b, width=0.3, ls='--', lw='3', color='#C00000')  # color显示rgb颜色
        ax1.set_xticks(range(len(year_list)))
        ax1.set_xticklabels(year_list)  # 可以旋转
        ax2 = ax1.twinx()
        p2 = ax2.plot(a, '-*', linewidth=2, color='#7F7F7F',
                      path_effects=[path_effects.SimpleLineShadow(), path_effects.Normal()])

        # ax2.set_ylim(0,max(a)*1.1)  # 这样就可以使另一个y轴从0开始，乘1.1设置顶部留空

        plt.title(u'均衡相对估值水平', fontproperties=font_set)  # 可以动态显示
        ax1.tick_params(direction='out', length=2, width=2)
        ax2.tick_params(direction='out', length=2, width=2, colors='#CD0000')
        ax1.set_xlabel(u'年份', fontproperties=font_set)

        ax1.yaxis.grid(linestyle='--')  # 只显示横线
        plt.legend((p1[0], p2[0]), (u'均衡市净率', u'均衡市盈率'), prop=font_set)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-equal_earning_and_market_rate-' + str(n) + 'year.svg')

    if search_img == '6':
        n = search_year # 年份数据
        a = []
        for i in range(n):
            if rs_finan[i].invturndays == None:
                a.append(0)
            else:
                a.append(rs_finan[i].invturndays)
        a.reverse()
        b = []
        for i in range(n):
            if rs_finan[i].arturndays == None:
                b.append(0)
            else:
                b.append(rs_finan[i].arturndays)
        b.reverse()
        c = []
        for i in range(n):
            if rs_finan[i].apturndays == None:
                c.append(0)
            else:
                c.append(rs_finan[i].apturndays)
        c.reverse()
        fig, ax1 = plt.subplots()

        x = np.arange(n)
        width = 0.15
        p1 = ax1.bar(x, a, width=width, color='#0070C0')
        p2 = ax1.bar(x + width + 0.05, b, width=width, color='#C00000')
        p3 = ax1.bar(x + width * 2 + 0.1, c, width=width, color='#7F7F7F')

        ax1.set_title(u'营运资本周转情况', fontproperties=font_set)
        ax1.set_xticks(x + width + 0.05)
        ax1.set_xticklabels(year_list)  # 可以旋转

        ax1.yaxis.grid(linestyle='--')  # 只显示横线
        ax1.tick_params(direction='out', length=3, width=3)  # 设置坐标轴上的小点儿

        plt.legend((p1[0], p2[0], p3[0]), (u'存货周转天数', u'应收账款周转天数', u'应付账款周转天数'), prop=font_set, loc='upper center',
                   bbox_to_anchor=(0.5, -0.05), ncol=3)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-invturndays_arturndays_apturndays-' + str(n) + 'year.svg')

    if search_img == '7': # 图：利润率状况
        n = search_year # 年份数据
        #这是设置x轴
        year_list = year_list

        fig, ax1 = plt.subplots()

        x = np.arange(n)
        # 数据集
        a=[]
        for i in range(n):
            if rs_finan[i].grossprofitmargin == None:
                a.append(0)
            else:
                a.append(rs_finan[i].grossprofitmargin)
        a.reverse()

        rs = finance_basics_add.query.filter(finance_basics_add.trade_code=='000895').order_by(finance_basics_add.the_year.desc()).all()
        # rs = rs_all[:10]
        b = [] #息税前利润率
        for i in range(n):
            if rs[i].ebit_rate == None:
                b.append(0)
            else:
                b.append(rs[i].ebit_rate*100)
        b.reverse()
        c = [] #净利润率
        for i in range(n):
            if rs[i].net_profit_rate == None:
                c.append(0)
            else:
                c.append(rs[i].net_profit_rate*100)
        c.reverse()

        p1 = ax1.plot(a,'-+',linewidth='2.5',color='#0070C0',path_effects=[path_effects.SimpleLineShadow(),path_effects.Normal()]) # '-o'是样式，前面不能写什么linestyle=
        p2 = ax1.plot(b,'-+',linewidth='2.5',color='#C00000',path_effects=[path_effects.SimpleLineShadow(),path_effects.Normal()])
        p3 = ax1.plot(c,'-+',linewidth='2.5',color='#7F7F7F',path_effects=[path_effects.SimpleLineShadow(),path_effects.Normal()])

        ax1.set_title(u'利润率状况',fontproperties=font_set)
        ax1.set_xticks(x)
        ax1.set_xticklabels(year_list) # 可以旋转

        ax1.yaxis.grid(linestyle='--') # 只显示横线
        ax1.tick_params(direction='out', length=3, width=3) # 设置坐标轴上的小点儿

        plt.legend((p1[0],p2[0],p3[0]),(u'毛利润率', u'息税前利润率', u'净利润率'),prop=font_set,loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)
        fig.set_size_inches(12,6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-profit_rate-' + str(n) + 'year.svg')

    if search_img == '8': #图 投入资本回报率ROIC与总资产收益率ROA
        n = search_year # 年份数据
        # rs = session.query(finance_basics_add).filter(finance_basics_add.trade_code == '000895').order_by(finance_basics_add.the_year.desc()).all()
        a = []
        for i in range(n):
            if rs[i].roic == None:
                a.append(0)
            else:
                a.append(rs[i].roic)
        a.reverse()
        b = []
        for i in range(n):
            if rs[i].rota == None:
                b.append(0)
            else:
                b.append((rs[i].rota*100))
        b.reverse()
        # 画图
        fig, ax1 = plt.subplots()

        x = np.arange(n)
        p1 = ax1.plot(a, '-+', linewidth='2.5', color='#7F7F7F', path_effects=[path_effects.SimpleLineShadow(),
                                                                               path_effects.Normal()])  # '-o'是样式，前面不能写什么linestyle=
        p2 = ax1.plot(b, '-+', linewidth='2.5', color='#C00000',
                      path_effects=[path_effects.SimpleLineShadow(), path_effects.Normal()])

        ax1.set_title(u'投入资本回报率ROIC 与 总资产收益率ROA （单位：百分比%）', fontproperties=font_set)
        ax1.set_xticks(x)
        ax1.set_xticklabels(year_list)  # 可以旋转

        ax1.yaxis.grid(linestyle='--')  # 只显示横线
        ax1.tick_params(direction='out', length=3, width=3)  # 设置坐标轴上的小点儿

        plt.legend((p1[0], p2[0]), (u'投入资本回报率', u'总资产收益率'), prop=font_set, loc='upper center',
                   bbox_to_anchor=(0.5, -0.05), ncol=2)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-roic_roa-' + str(n) + 'year.svg')

    if search_img == '9':
        n = search_year # 年份数据
        # 设置x轴
        year_list = year_list

        # 这是数据集
        # rs = finance_basics_add.query.filter(finance_basics_add.trade_code == '000895').order_by(finance_basics_add.the_year.desc()).all()

        a = []  # 资产总计：tot_assets
        for i in range(n):
            if rs[i].tot_assets == None:
                a.append(0)
            else:
                a.append(round(rs[i].tot_assets / 100000000))
        a.reverse()

        b = []  # 总资产周转率：tot_assets_turnover
        for i in range(n):
            if rs[i].tot_assets_turnover == None:
                b.append(0)
            else:
                b.append(rs[i].tot_assets_turnover)
        b.reverse()

        # 设置双y轴
        fig, ax1 = plt.subplots()
        p1 = ax1.bar(range(len(a)), a, width=0.3, ls='--', lw='3', color='#A6A6A6')  # color显示rgb颜色
        # !*! 这样才能显示x轴
        ax1.set_xticks(range(len(year_list)))
        ax1.set_xticklabels(year_list)  # 可以旋转

        ax2 = ax1.twinx()
        p2 = ax2.plot(b, '-*', linewidth=2, color='#0070C0',
                      path_effects=[path_effects.SimpleLineShadow(), path_effects.Normal()])

        # ax2.set_ylim(0, int(max(b))+1)  # 这样就可以使另一个y轴从0开始;设置顶部留空
        plt.title(u'资产规模 与 总资产周转率', fontproperties=font_set)  # 可以动态显示
        # ax1.set_xtitle('Sharing Y axis') 另一种方法

        ax1.tick_params(direction='out', length=2, width=2)
        ax2.tick_params(direction='out', length=2, width=2, colors='b')

        ax2.yaxis.grid(linestyle='--')  # 只显示横线
        plt.legend((p1[0], p2[0]), (u'资产总计（单位：亿元）', u'总资产周转率'), prop=font_set, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                   ncol=2)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-tot_assets_and_turnover-' + str(n) + 'year.svg')

    if search_img == '10': # 图：净资产与净资产收益率ROE
        n = search_year # 年份数据
        # 这是设置x轴
        year_list = year_list

        a = []  # 净资产
        for i in range(n):
            if rs[i].net_assets == None:
                a.append(0)
            else:
                a.append(round(rs[i].net_assets / 100000000))
        a.reverse()

        b = []  # 净资产收益率ROE(总额 roe_tot)
        for i in range(n):
            if rs[i].roe_tot == None:
                b.append(0)
            else:
                b.append(rs[i].roe_tot * 100)
        b.reverse()

        # 设置双y轴
        fig, ax1 = plt.subplots()
        p1 = ax1.bar(range(len(a)), a, width=0.3, ls='--', lw='3', color='#C00000')  # color显示rgb颜色
        # !*! 这样才能显示x轴
        ax1.set_xticks(range(len(year_list)))
        ax1.set_xticklabels(year_list)  # 可以旋转

        ax2 = ax1.twinx()
        p2 = ax2.plot(b, '-*', linewidth=2.5, color='#7F7F7F',
                      path_effects=[path_effects.SimpleLineShadow(), path_effects.Normal()])
        # 总报错 ax2.set_ylim(0, max(b) * 1.1)  # 这样就可以使另一个y轴从0开始，乘1.1设置顶部留空

        plt.title(u'净资产 与 净资产收益率ROE', fontproperties=font_set)  # 可以动态显示
        # ax1.set_xtitle('Sharing Y axis') 另一种方法

        ax1.tick_params(direction='out', length=2, width=2)
        ax2.tick_params(direction='out', length=2, width=2)
        # ax2.set_ylim(0, int(max(b))*1.2)  # 这样就可以使另一个y轴从0开始；设置顶部留空
        ax2.yaxis.grid(linestyle='--')  # 只显示横线
        plt.legend((p1[0], p2[0]), (u'净资产（单位：亿元）', u'净资产收益率ROE（单位：百分比%）'), prop=font_set, loc='upper center',
                   bbox_to_anchor=(0.5, -0.05), ncol=2)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-net_assets_and_roe-' + str(n) + 'year.svg')

    if search_img == '11':
        n = search_year # 年份数据
        # 这是设置x轴
        year_list = year_list

        fig, ax = plt.subplots()

        a = []
        for i in range(n):
            if rs_finan[i].operatecashflow_ttm2 == None or rs_finan[i].operatecashflow_ttm2==0 :
                a.append(0)
            else:
                a.append(round(rs_finan[i].operatecashflow_ttm2/100000000))
        a.reverse()

        b = []
        for i in range(n):
            if rs_finan[i].investcashflow_ttm2 == None or rs_finan[i].investcashflow_ttm2 ==0:
                b.append(0)
            else:
                b.append(round(rs_finan[i].investcashflow_ttm2/100000000))
        b.reverse()

        c = []
        for i in range(n):
            if rs_finan[i].financecashflow_ttm2 == None or rs_finan[i].financecashflow_ttm2 == 0 :
                c.append(0)
            else:
                c.append(round(rs_finan[i].financecashflow_ttm2/100000000))
        c.reverse()

        x = np.arange(n)
        width = 0.15

        p1 = plt.bar(np.array(range(len(a))), a, width=width, color='#C00000')
        p2 = plt.bar(np.array(range(len(b))) + width + 0.05, b, width=width, color='#0070C0')
        p3 = plt.bar(np.array(range(len(c))) + width * 2 + 0.1, c, width=width, color='#7F7F7F')

        ax.set_title(u'现金流状况（单位：亿元）', fontproperties=font_set)

        ax.set_xticks(x + width + 0.05)  # 设置年份坐标在中间显示
        ax.set_xticklabels(year_list)  # 可以旋转
        ax.tick_params(direction='out', length=2, width=2)

        ax.yaxis.grid(linestyle='--')  # 只显示横线

        plt.legend((p1[0], p2[0], p3[0]), (u'经营活动现金流', u'投资活动现金流', u'筹资活动现金流'), prop=font_set, loc='upper center',
                   bbox_to_anchor=(0.5, -0.05), ncol=3)
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-cashflow-' + str(n) + 'year.svg')

    if search_img == '12':
        n = search_year # 年份数据
        # 这是做数据集
        a = []
        for i in range(n):
            if rs_inves[i].employee == None:
                a.append(0)
            else:
                a.append(rs_inves[i].employee)
        a.reverse()

        fig, ax = plt.subplots()

        x = np.arange(n)
        width = 0.3
        plt.bar(np.array(range(len(a))), a, width=width, color='#A6A6A6')
        ax.set_title(u'雇员数量', fontproperties=font_set)
        ax.set_xticks(x)  # 设置年份坐标在中间显示
        ax.set_xticklabels(year_list)  # 可以旋转
        ax.tick_params(direction='out', length=2, width=2)
        ax.yaxis.grid(linestyle='--')  # 只显示横线
        fig.set_size_inches(12, 6)
        plt.savefig('F:/flask/MasteringFlask/webapp/static/graph/' + trade_code + '-employee-' + str(n) + 'year.svg')

    return render_template("stock_solo/stock_solo_graph.html",current_user=current_user,graph_form=graph_form,trade_code=trade_code, n=search_year, search_img=search_img)

@stocksolo_blueprint.route('/test',methods=('GET','POST'))
@stocksolo_blueprint.route('/test/<string:graph_id>',methods=('GET','POST'))
def mytest(graph_id=1):
    graph_id = request.form.get('graph_id')
    form = graph_Form()
    return render_template('stock_solo/test.html',form=form,graph_id=graph_id)

