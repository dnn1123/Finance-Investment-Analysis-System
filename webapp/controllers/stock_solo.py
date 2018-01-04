#coding=utf-8
from flask import Blueprint,redirect,render_template,url_for,request, jsonify,session
from os import path
from webapp.models import *
from webapp.forms import CodeForm
from flask_login import login_required,current_user
from webapp.extensions import finance_analyst_permission # 这个就是经济师权限
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import MySQLdb,time,re #re用于判断是否含中文
import numpy as np
import restfulapi
from webapp.decorators import admin_required,permission_required

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

def basic(data):
    if data=="":
        if session.has_key('stockcode'):
            data = session['stockcode']
        else:
            data = '000001'
    if (request.method == 'POST'):
        stockcode=request.form.get("stockcode","000001")
        session['stockcode'] = stockcode
        return redirect(url_for('stock_solo.basic', current_user=current_user, data=stockcode))
    match = zhPattern.search(data)
    if match:
        stock = stock_basics.query.filter_by(sec_name=data).first_or_404()
    else:
        stock = stock_basics.query.filter_by(trade_code=data).first_or_404()
    return render_template("stock_solo/stock_solo_basic.html", current_user=current_user,stock=stock)

@stocksolo_blueprint.route('/finance_data',methods=('GET','POST'))
@stocksolo_blueprint.route('/finance_data/<string:data>',methods=('GET','POST'))
@login_required
def finance_data(data='000895'):
    data=data
    form = CodeForm()
    if form.validate_on_submit():
        data = form.code.data
        return redirect(url_for('stock_solo.finance_data', current_user=current_user, data=data))
    match = zhPattern.search(data)
    if match:
        stock = stock_basics.query.filter_by(sec_name=data).first_or_404()
    else:
        stock = stock_basics.query.filter_by(trade_code=data).first_or_404()
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

@stocksolo_blueprint.route('/finance_data_yc', methods=('GET', 'POST'))
@stocksolo_blueprint.route('/finance_data_yc/<string:data>', methods=('GET', 'POST'))
@login_required
@permission_required(Permission.trader)
def finance_data_yc(data='000001'):
    if session.has_key('stockcode'):
        data = session['stockcode']
    else:
        data = '000001'
    if (request.method == 'POST'):
        stockcode = request.form.get("stockcode","000001")
        session['stockcode'] = stockcode
        return redirect(url_for('stock_solo.finance_data_yc', current_user=current_user, data=stockcode))
    return render_template("stock_solo/stock_solo_finance_data_yc.html",current_user=current_user,stockcode="\""+data+"\"")


@stocksolo_blueprint.route('/compare', methods=('GET', 'POST'))
@stocksolo_blueprint.route('/compare/<string:data>', methods=('GET', 'POST'))
@login_required
def compare():
    return render_template("stock_solo/stock_solo_compare.html",current_user=current_user)

@stocksolo_blueprint.route('/invest_value',methods=('GET','POST'))
@stocksolo_blueprint.route('/invest_value/<string:data>',methods=('GET','POST'))
# @login_required

def invest_value(data='000001'):
    if session.has_key('stockcode'):
        data = session['stockcode']
    else:
        data = '000001'
    if (request.method == 'POST'):
        stockcode=request.form.get("stockcode","000001")
        session['stockcode'] = stockcode
        return redirect(url_for('stock_solo.invest_value', current_user=current_user, data=stockcode))
    return render_template("stock_solo/finance_data.html",stockcode="\""+data+"\"")
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