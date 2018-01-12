# encoding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify, flash
from webapp.models import *
import MySQLdb, time, re
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me
from flask_login import current_user
import string
from collections import Counter
import tushare as ts
import gc
import pandas as pd
from datetime import datetime
from datetime import timedelta
from  webapp.stratlib import *

api_blueprint = Blueprint(
        'restfulapi',
        __name__,
        url_prefix='/api'
)

@api_blueprint.route("/admin/", methods=('GET', 'POST'))
def admin():
    stockcode = request.args.get('code')
    results = users_roles.query.all()
    name_list = []
    permission_list = []
    for result in results:
        name_list.append(result.user_name)
        permission_list.append(result.permissions)
    data = {
        'name_list':name_list,
        "permission_list":permission_list
    }
    return jsonify(data)

# 数据库查询api 用于Ajax数据返回 json格式数据
@api_blueprint.route("/finance_data/", methods=('GET', 'POST'))
def finance_data():
    stockcode = request.args.get('stockcode')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')
    filters = {
        finance_basics.trade_code == stockcode,
        finance_basics.the_year >= starttime,
        finance_basics.the_year <= endtime,
    }
    results = finance_basics.query.filter(*filters).all()
    result1 = finance_basics.query.filter_by(trade_code=stockcode).first_or_404()

    data = {}
    year_list = []
    data['the_name'] = result1.sec_name
    for index in indexes:
        exec (index + "_list=[]")

    for result in results:
        year_list.append(result.the_year)
        for index in indexes:
            if eval("result." + index) is None:
                exec (index + "_list.append(result." + index + ")")
            else:
                exec (index + "_list.append(float(result." + index + "))")

    data['stock_code'] = stockcode
    data['the_year'] = year_list
    data['indexes'] = indexes
    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/code_wind/", methods=('GET', 'POST'))
def code_wind():
    code_list = request.args.getlist('codelist[]')

    data = {}

    data['codelist'] = code_list

    return jsonify(data)

    # user_name = current_user.username
    # codelist = []
    # results = favorite_code.query.filter_by(user_name=user_name).all()
    # for result in results:
    #     code_list.append(result.code)

    # wind_4 = []
    # wind_3 = []
    # wind_2 = []
    # wind_1 = []
    # for code in codelist:
    #     result = cns_stock_industry.query.filter_by(trade_code=code).first_or_404()
    #     wind_4.push(result.industry_gics_4)
    #     result4 = cns_sub_industry.query.filter_by(industry_gicscode_4=result.industry_gicscode_4).first_or_404()
    #     result3 = cns_industry.query.filter_by(industry_gicscode_3=result4.belong).first_or_404()
    #     wind_3.push(result3.industry_gics_3)
    #     result2 = cns_group_industry.query.filter_by(industry_gicscode_2=result3.belong).first_or_404()
    #     wind_2.push(result2.industry_gics_2)
    #     result1 = cns_department_industry.query.filter_by(industry_gicscode_1=result2.belong).first_or_404()
    #     wind_1.push(result1.industry_gics_1)

    # 'wind_4': wind_4,
    # 'wind_3': wind_3,
    # 'wind_2': wind_2,
    # 'wind_1': wind_1,
    # 'codelist':stockcode

@api_blueprint.route('/change_permission', methods=('GET', 'POST'))
def change_permission():
    name = request.form.get('name')
    permission = request.form.get('permission')

    old_users_roles =  users_roles.query.filter_by(user_name=name).first()
    db.session.delete(old_users_roles)
    db.session.commit()

    n_users_roles =  users_roles(user_name=name)
    n_users_roles.permissions = permission
    db.session.add(n_users_roles)
    db.session.commit()
    data={
        'name':name,
        'permission':permission
    }
    return jsonify(data)

@api_blueprint.route('/get_ajax_compare', methods=('GET', 'POST'))
def get_ajax_compare():
    code = request.form.get('code')
    date = request.form.getlist('date[]')
    indexes = request.form.getlist('index[]')
    the_year_start = int(date[0][0:4] + '1231')
    the_year_end = int(date[1][0:4] + '1231')
    data = {}
    test = {}
    year_list = []
    year_list1 = []
    the_name_list = []
    the_year = the_year_end
    while the_year >= the_year_start:
        year_list.append(the_year)
        year_list1.append(the_year / 10000)
        the_year = the_year - 10000
    result1 = finance_basics.query.filter_by(trade_code=code).first_or_404()
    data['the_name'] = result1.sec_name
    for index in indexes:
        results = []
        for year in year_list:
            if index == 'ebit_rate':
                result = finance_basics_add.query.filter_by(trade_code=code, the_year=year).first_or_404()
                if eval('result.' + index) is None:
                    results.append('..')
                else:
                    results.append(str(eval('result.' + index)))
            else:
                result = finance_basics.query.filter_by(trade_code=code, the_year=year).first_or_404()
                if eval('result.' + index) is None:
                    results.append('..')
                else:
                    results.append(str(eval('result.' + index)))
        data[index] = results
    data['the_code'] = code
    data['indexs'] = indexes
    data['the_year_list'] = year_list1

    return jsonify(data)


@api_blueprint.route('/get_ajax', methods=('GET', 'POST'))
def get_ajax():
    code = request.form.get('code')
    date = request.form.getlist('date[]')
    indexes = request.form.getlist('selected[]')

    the_year_start = int(date[0][0:4] + '1231')
    the_year_end = int(date[1][0:4] + '1231')

    data = {}
    year_list = []
    year_list1 = []
    the_year = the_year_end
    while the_year >= the_year_start:
        year_list.append(the_year)
        year_list1.append(the_year / 10000)
        the_year = the_year - 10000

    result1 = finance_basics.query.filter_by(trade_code=code).first_or_404()
    data['the_name'] = result1.sec_name

    for index in indexes:
        results = []
        for year in year_list:
            if index == 'ebit_rate':
                result = finance_basics_add.query.filter_by(trade_code=code, the_year=year).first_or_404()
                if eval('result.' + index) is None:
                    results.append('..')
                else:
                    results.append(str(eval('result.' + index)))
            else:
                result = finance_basics.query.filter_by(trade_code=code, the_year=year).first_or_404()
                if eval('result.' + index) is None:
                    results.append(0)
                else:
                    results.append(str(eval('result.' + index)))

        data[index] = results
    data['indexs'] = indexes
    data['the_code'] = code
    data['the_year_list'] = year_list1
    return jsonify(data)


@api_blueprint.route('/iscode', methods=('GET', 'POST'))
def iscode():
    data = {}
    code = request.form.get('code')
    result1 = finance_basics.query.filter_by(trade_code=code).first()
    if (result1):
        data['the_name'] = result1.sec_name
    else:
        data['the_name'] = 'false'
    data['the_code'] = code
    return jsonify(data)


@api_blueprint.route("/finance_data_new/", methods=('GET', 'POST'))
def finance_data_new():
    stockcode = request.args.getlist('stockcode[]')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')
    data = {}
    year_list = []
    the_year_start = int(starttime[0:4])
    the_year_end = int(endtime[0:4])
    the_year = the_year_end
    while the_year >= the_year_start:
        year_list.append(the_year)
        # year_list1.append(the_year / 10000)
        the_year = the_year - 1
    for index in indexes:
        exec (index + "_list=[]")
    data['the_name'] = []
    for code in stockcode:
        filters = {
            finance_basics.trade_code == code,
            finance_basics.the_year >= starttime,
            finance_basics.the_year <= endtime,
        }
        results = finance_basics.query.filter(*filters).all()
        result1 = finance_basics.query.filter_by(trade_code=code).first_or_404()
        data['the_name'].append(result1.sec_name)
        for result in results:
            # year_list.append(result.the_year)
            for index in indexes:
                if eval("result." + index) is None:
                    exec (index + "_list.append(result." + index + ")")
                else:
                    exec (index + "_list.append(float(result." + index + "))")

    data['stock_code'] = stockcode
    data['the_year'] = year_list
    data['indexes'] = indexes
    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/invest_data_new/", methods=('GET', 'POST'))
def invest_data_new():
    stockcode = request.args.getlist('stockcode[]')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')
    data = {}
    year_list = []
    the_year_start = int(starttime[0:4])
    the_year_end = int(endtime[0:4])
    the_year = the_year_end
    while the_year >= the_year_start:
        year_list.append(the_year)
        # year_list1.append(the_year / 10000)
        the_year = the_year - 1
    for index in indexes:
        exec (index + "_list=[]")
    for code in stockcode:
        filters = {
            invest_values.trade_code == code,
            invest_values.the_year >= starttime,
            invest_values.the_year <= endtime,
        }
        results = invest_values.query.filter(*filters).all()
        for result in results:
            # year_list.append(result.the_year)
            for index in indexes:
                if eval("result." + index) is None:
                    exec (index + "_list.append(result." + index + ")")
                else:
                    exec (index + "_list.append(float(result." + index + "))")
    data['stock_code'] = stockcode
    data['the_year'] = year_list
    data['the_year'] = year_list
    data['indexes'] = indexes
    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/invest_data/", methods=('GET', 'POST'))
def invest_data():
    stockcode = request.args.get('stockcode')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')

    filters = {
        invest_values.trade_code == stockcode,
        invest_values.the_year >= starttime,
        invest_values.the_year <= endtime,
    }
    results = invest_values.query.filter(*filters).all()

    data = {}
    year_list = []

    for index in indexes:
        exec (index + "_list=[]")

    for result in results:
        year_list.append(result.the_year)
        for index in indexes:
            if eval("result." + index) is None:
                exec (index + "_list.append(result." + index + ")")
            else:
                exec (index + "_list.append(float(result." + index + "))")
    data['stock_code'] = stockcode
    data['the_year'] = year_list
    data['indexes'] = indexes
    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/market_value/", methods=('GET', 'POST'))
def market_value():
    data = {}
    province = request.args.get('province')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')

    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()

    year_list = []
    for year in years:
        year_list.append(year.the_year)
    # yc
    if province == 'all':
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.net_assets).label("net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                           finance_basics_add.the_year.label("the_year")).group_by(finance_basics_add.the_year).all()
    else:
        filters = {
            stock_basics.province.like("%" + province + "%")
        }
        results = stock_basics.query.filter(or_(*filters)).all()
        code_list = []
        for result in results:
            code_list.append(result.trade_code)
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.net_assets).label("net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                           finance_basics_add.the_year.label("the_year")).filter(
                finance_basics_add.trade_code.in_(code_list)).group_by(finance_basics_add.the_year).all()

        # yc_end


        # yc
        # value_list = []
        # for index in indexes:
        #     exec (index + "_list=[]")
        # for index in indexes:
        #     exec (index + "_value=0")
        # for year in year_list:
        #     # value = 0
        #     for code in code_list:
        #         Filters = {
        #             finance_basics_add.trade_code == code,
        #             finance_basics_add.the_year == year,
        #         }
        #         result = finance_basics_add.query.filter(*Filters).first()
        #         for index in indexes:
        #             if eval("result." + index) is not None:
        #                 exec (index+"_value += float(result." + index + "/100000000)")
        #             else:
        #                 exec (index+"_value += 0")
        #     for index in indexes:
        #         exec (index + "_list.append(" + str(index+"_value")+")")
        #
        # for index in indexes:
        #     exec ("data['" + index + "']=" + index + "_list")


        # zyq
    rs_list = range(len(rs))
    rs_list.reverse()
    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")
    for x in rs_list:
        for index in indexes:
            if eval("rs[x]." + index) is not None:
                exec ("my" + index + "= float((rs[x]." + index + ")/100000000)")
            else:
                exec ("my" + index + "= 0 ")
            exec (index + "_list.append(my" + index + ")")
    data['the_year'] = year_list
    data['indexes'] = indexes
    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/market_one/", methods=('GET', 'POST'))
def market_one():
    time = request.args.get('time')
    province = request.args.get('province')
    indexes = request.args.getlist('indexes[]')
    codes = ['10', '15', '20', '25', '30', '35', '40', '45', '55', '60']
    # yc
    if province == 'all':
        results = stock_basics.query.filter().all()
    else:
        filters = {
            stock_basics.province.like("%" + province + "%")
        }
        results = stock_basics.query.filter(or_(*filters)).all()
    code_list = []
    for result in results:
        code_list.append(result.trade_code)
    # yc_end
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    data_list = []

    for code in codes:
        results = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                                func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                                func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                                func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                                cns_department_industry.industry_gics_1.label("industry_gics_1")).filter(
                finance_basics_add.the_year == time).filter(
                finance_basics_add.trade_code.in_(code_list)).filter(
                cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
                cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
                cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
                cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
                cns_department_industry.industry_gicscode_1 == code).all()
        for result in results:
            for index in indexes:
                if eval("result." + index) is not None:
                    exec ("my" + index + "= float((result." + index + ")/100000000)")
                else:
                    exec ("my" + index + "= 0 ")
                exec ("data_list.append(my" + index + ")")

    data = {}
    data['my_code'] = codes
    data['my_num'] = data_list

    return jsonify(data)


@api_blueprint.route("/market_bar/", methods=('GET', 'POST'))
def market_bar():
    time = request.args.get('time')
    indexes = request.args.getlist('indexes[]')

    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    results = session.query(finance_basics_add.tot_oper_rev.label("tot_oper_rev"),
                            finance_basics_add.net_profit_is.label("net_profit_is"),
                            finance_basics_add.wgsd_net_inc.label("wgsd_net_inc"),
                            finance_basics_add.tot_assets.label("tot_assets"),
                            finance_basics_add.tot_liab.label("tot_liab"),
                            finance_basics_add.net_assets.label("net_assets"),
                            finance_basics_add.wgsd_com_eq.label("wgsd_com_eq"),
                            finance_basics_add.operatecashflow_ttm2.label("operatecashflow_ttm2"),
                            finance_basics_add.investcashflow_ttm2.label("investcashflow_ttm2"),
                            finance_basics_add.financecashflow_ttm2.label("financecashflow_ttm2"),
                            finance_basics_add.cashflow_ttm2.label("cashflow_ttm2"),
                            finance_basics_add.free_cash_flow.label("free_cash_flow"),
                            finance_basics_add.the_year.label("the_year"),
                            finance_basics_add.trade_code.label("trade_code")).filter(
            finance_basics_add.the_year == time).all()

    x_list = []
    for index in indexes:
        exec (index + "_list=[]")

    for result in results:
        x_list.append(result.trade_code)
    for index in indexes:
        if eval("result." + index) is not None:
            exec ("my" + index + "= float((result." + index + ")/100000000)")
        else:
            exec ("my" + index + "= 0 ")
        exec (index + "_list.append(my" + index + ")")

    data = {}
    data['my_code'] = x_list
    data['indexes'] = indexes

    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")

    return jsonify(data)


@api_blueprint.route("/market_status1/", methods=('GET', 'POST'))
def market_status1():
    data = {}

    code = request.args.get('code')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')

    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()
    year_list = []
    for year in years:
        year_list.append(year.the_year)

    rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                       func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                       func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                       func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                       func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       cns_department_industry.industry_gics_1.label("industry_gics_1")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
            cns_department_industry.industry_gicscode_1 == code).group_by(
            finance_basics_add.the_year).all()
    rs_list = range(len(rs))
    rs_list.reverse()

    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")

    for x in rs_list:
        for index in indexes:
            if eval("rs[x]." + index) is not None:
                exec ("my" + index + "= float((rs[x]." + index + ")/100000000)")
            else:
                exec ("my" + index + "= 0 ")
            exec (index + "_list.append(my" + index + ")")

    data['the_year'] = year_list
    data['indexes'] = indexes
    data['the_code'] = code

    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/market_status2/", methods=('GET', 'POST'))
def market_status2():
    data = {}

    code = request.args.get('code')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')

    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()
    year_list = []
    for year in years:
        year_list.append(year.the_year)

    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")

    rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                       func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                       func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                       func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                       func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       cns_group_industry.industry_gics_2.label("industry_gics_2")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_group_industry.industry_gicscode_2 == code).group_by(finance_basics_add.the_year).all()
    rs_list = range(len(rs))
    rs_list.reverse()

    for x in rs_list:
        for index in indexes:
            if eval("rs[x]." + index) is not None:
                exec ("my" + index + "= float((rs[x]." + index + ")/100000000)")
            else:
                exec ("my" + index + "= 0 ")
            exec (index + "_list.append(my" + index + ")")

    data['the_year'] = year_list
    data['indexes'] = indexes
    data['the_code'] = code

    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/market_status3/", methods=('GET', 'POST'))
def market_status3():
    data = {}

    code = request.args.get('code')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')

    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()
    year_list = []
    for year in years:
        year_list.append(year.the_year)

    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")

    rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                       func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                       func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                       func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                       func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       cns_industry.industry_gics_3.label("industry_gics_3")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.industry_gicscode_3 == code).group_by(finance_basics_add.the_year).all()
    rs_list = range(len(rs))
    rs_list.reverse()

    for x in rs_list:
        for index in indexes:
            if eval("rs[x]." + index) is not None:
                exec ("my" + index + "= float((rs[x]." + index + ")/100000000)")
            else:
                exec ("my" + index + "= 0 ")
            exec (index + "_list.append(my" + index + ")")

    data['the_year'] = year_list
    data['indexes'] = indexes
    data['the_code'] = code

    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


@api_blueprint.route("/market_status4/", methods=('GET', 'POST'))
def market_status4():
    data = {}

    code = request.args.get('code')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')

    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()
    year_list = []
    for year in years:
        year_list.append(year.the_year)

    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")

    rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                       func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                       func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                       func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                       func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       cns_sub_industry.industry_gicscode_4,
                       cns_sub_industry.industry_gics_4.label("industry_gics_4")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.industry_gicscode_4 == code).group_by(finance_basics_add.the_year).all()
    rs_list = range(len(rs))
    rs_list.reverse()

    for x in rs_list:
        for index in indexes:
            if eval("rs[x]." + index) is not None:
                exec ("my" + index + "= float((rs[x]." + index + ")/100000000)")
            else:
                exec ("my" + index + "= 0 ")
            exec (index + "_list.append(my" + index + ")")

    data['the_year'] = year_list
    data['indexes'] = indexes
    data['the_code'] = code

    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)


# 用于股票代码自动补全
@api_blueprint.route("/stock_code/", methods=('GET', 'POST'))
def stock_code():
    stockcode = request.args.get('q')
    filters = {
        stock_basics.trade_code.like("%" + stockcode + "%"),
        stock_basics.sec_name.like("%" + stockcode + "%")
    }
    results = stock_basics.query.filter(or_(*filters)).all()
    data = {}
    stockcode_list = []
    secname_list = []
    for result in results:
        stockcode_list.append(result.trade_code)
        secname_list.append(result.sec_name)
    data['stockcode'] = stockcode_list
    data['stockname'] = secname_list
    return jsonify(data)


@api_blueprint.route("/gics_1/", methods=('GET', 'POST'))
def gics_1():
    results = cnsb_department_industry.query.all()
    list = []
    for result in results:
        list.append({"gicscode1": result.industry_gicscode_1, "gics1": result.industry_gics_1})
    return jsonify(list)


@api_blueprint.route("/gics_2/", methods=('GET', 'POST'))
def gics_2():
    code = request.args.get("code")
    filters = {
        cnsb_group_industry.belong == code
    }
    results = cnsb_group_industry.query.filter(*filters).all()
    list = []
    for result in results:
        list.append({"gicscode2": result.industry_gicscode_2, "gics2": result.industry_gics_2})
    return jsonify(list)


@api_blueprint.route("/gics_3/", methods=('GET', 'POST'))
def gics_3():
    code = request.args.get("code")
    filters = {
        cnsb_industry.belong == code
    }
    results = cnsb_industry.query.filter(*filters).all()
    list = []
    for result in results:
        list.append({"gicscode3": result.industry_gicscode_3, "gics3": result.industry_gics_3})
    return jsonify(list)


@api_blueprint.route("/gics_4/", methods=('GET', 'POST'))
def gics_4():
    code = request.args.get("code")
    filters = {
        cnsb_sub_industry.belong == code
    }
    results = cnsb_sub_industry.query.filter(*filters).all()
    list = []
    for result in results:
        list.append({"gicscode4": result.industry_gicscode_4, "gics4": result.industry_gics_4})
    return jsonify(list)


@api_blueprint.route("/update_gics/", methods=('GET', 'POST'))
def update_gics():
    trade_code = request.values.get("trade_code")
    gics_4 = request.values.get('gics_4')
    gics_name = request.values.get('gics_name')
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    session.query(cns_stock_industry).filter(cns_stock_industry.trade_code == trade_code).update(
            {'belong': gics_4, 'industry_gicscode_4': gics_4, 'industry_gics_4': gics_name})  # 改为belong
    session.commit()  # 少写了这一行，所以修改没成功
    return "true"


@api_blueprint.route("/update_gicsb/", methods=('GET', 'POST'))
def update_gicsb():
    trade_code = request.values.get("trade_code")
    gics_4 = request.values.get('gics_4')
    gics_name = request.values.get('gics_name')
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    session.query(cnsb_stock_industry).filter(cnsb_stock_industry.trade_code == trade_code).update(
            {'industry_gicscode_4': gics_4, 'industry_gics_4': gics_name})  # 改为belong
    session.commit()  # 少写了这一行，所以修改没成功
    return "true"


# 显示“主营业务”详情
@api_blueprint.route('/cns_business_detail/', methods=('GET', 'POST'))
def cns_business_detail():  # 需要这个默认trade_code吗？
    trade_code = request.args.get("trade_code")  # 哈哈，成功了！！
    result = cns_stock_industry.query.filter_by(trade_code=trade_code).first()
    return result.business


@api_blueprint.route('/personal/add_code', methods=['GET', 'POST'])
def add_code():
    if (request.method == 'POST'):
        stockcode = request.form.get("stockcode", "000001")
        new_fcode = favorite_code()
        new_fcode.user_name = current_user.username
        new_fcode.code = stockcode
        db.session.add(new_fcode)
        db.session.commit()
        flash(
                "添加成功",
                category="success"
        )
        return redirect(url_for('main.personal'))


@api_blueprint.route('/personal/add_code_fd_yc', methods=['GET', 'POST'])
def add_code_fd_yc():
    data = {}
    stockcode = request.form.get('code')
    new_fcode = favorite_code()
    new_fcode.user_name = current_user.username
    new_fcode.code = stockcode
    db.session.add(new_fcode)
    db.session.commit()
    data['value'] = 'success'
    return jsonify(data)


@api_blueprint.route('/personal/wind', methods=['GET', 'POST'])
def wind():
    stockcode = request.args.getlist('stockcode[]')
    wind_4 = []
    wind_3 = []
    wind_2 = []
    wind_1 = []
    for code in stockcode:
        result = cns_sub_industry.query.filter_by(trade_code=code).first_or_404()
        wind_4.push(result.industry_gics_4)
        result4 = cns_sub_industry.query.filter_by(industry_gicscode_4=result.industry_gicscode_4).first_or_404()
        result3 = cns_industry.query.filter_by(industry_gicscode_3=result4.belong).first_or_404()
        wind_3.push(result3.industry_gics_3)
        result2 = cns_group_industry.query.filter_by(industry_gicscode_2=result3.belong).first_or_404()
        wind_2.push(result2.industry_gics_2)
        result1 = cns_department_industry.query.filter_by(industry_gicscode_1=result2.belong).first_or_404()
        wind_1.push(result1.industry_gics_1)
    data = {
        'wind_4': wind_4,
        'wind_3': wind_3,
        'wind_2': wind_2,
        'wind_1': wind_1
    }
    return jsonify(data)


@api_blueprint.route('/personal/delete_code', methods=['GET', 'POST'])
def delete_code():
    data = {}
    code_delete_list = request.form.getlist('selected[]')
    for code in code_delete_list:
        result = favorite_code.query.filter_by(user_name=current_user.username, code=code).first()
        # new_fcode1 = favorite_code()
        # new_fcode1.user_name = current_user.username
        # new_fcode1.code = code
        db.session.delete(result)
        db.session.commit()
    data['a'] = 1
    return jsonify(data)


@api_blueprint.route('/personal/search', methods=['GET', 'POST'])
def search():
    data = {}
    user_name = current_user.username
    code_list = []
    name_list = []
    count_list = []
    results = favorite_code.query.filter_by(user_name=user_name).all()
    for result in results:
        code_list.append(result.code)
        result1 = finance_basics.query.filter_by(trade_code=result.code).first_or_404()
        result2 = favorite_code.query.filter_by(code=result.code).count()
        # count=len(result2)
        # data=favorite_code.query.filter_by(code=stockcode).all()
        # count=len(data)
        name_list.append(result1.sec_name)
        count_list.append(result2)
    wind_4 = []
    wind_3 = []
    wind_2 = []
    wind_1 = []
    for code in code_list:
        result = cns_stock_industry.query.filter_by(trade_code=code).first_or_404()
        wind_4.append(result.industry_gics_4)
        result4 = cns_sub_industry.query.filter_by(industry_gicscode_4=result.industry_gicscode_4).first_or_404()
        result3 = cns_industry.query.filter_by(industry_gicscode_3=result4.belong).first_or_404()
        wind_3.append(result3.industry_gics_3)
        result2 = cns_group_industry.query.filter_by(industry_gicscode_2=result3.belong).first_or_404()
        wind_2.append(result2.industry_gics_2)
        result1 = cns_department_industry.query.filter_by(industry_gicscode_1=result2.belong).first_or_404()
        wind_1.append(result1.industry_gics_1)

    citycount = {}
    for code in code_list:
        city = stock_basics.query.filter_by(trade_code=code).first().city
        if (citycount.has_key(city)):
            citycount[city] += 1
        else:
            citycount[city] = 1
    cityrec = []
    for key in citycount:
        rec = [key, citycount[key]]
        cityrec.append(rec)

    data['wind_4'] = Counter(wind_4)
    data['wind_3'] = Counter(wind_3)
    data['wind_2'] = Counter(wind_2)
    data['wind_1'] = Counter(wind_1)
    data['code_list'] = code_list
    data['name_list'] = name_list
    data['user_name'] = current_user.username
    data['count_list'] = count_list
    data['cityrec'] = cityrec
    return jsonify(data)


@api_blueprint.route('/personal/is_repeatcode', methods=['GET', 'POST'])
def is_repeatcode():
    data = {}
    code = request.form.get('code')
    result = favorite_code.query.filter_by(user_name=current_user.username, code=code).first()
    if result:
        data['exit'] = 'true'
    else:
        data['exit'] = 'flase'
    return jsonify(data)


@api_blueprint.route('/buyStock', methods=['GET', 'POST'])
def buystock():
    username = current_user.username
    date = request.form.get('date')
    code = request.form.get('codeName')
    price = string.atof(request.form.get('price').encode("utf-8"))
    amount = string.atof(request.form.get('amount').encode("utf-8"))
    commission = string.atof(request.form.get('commission').encode("utf-8"))

    result = investment_portfolio.query.filter_by(user_name=current_user.username, code=code).first()
    if (result is None):
        new_data = investment_portfolio()
        new_data.user_name = current_user.username
        new_data.code = code
        new_data.shares = amount
        new_data.total_cost = price * amount * (1 + commission) / amount  # average cost per share
        db.session.add(new_data)
        db.session.commit()
    else:
        result.total_cost = (result.total_cost * result.shares + price * amount * (1 + commission)) / (
            result.shares + amount)  # average cost per share
        result.shares = result.shares + amount
        db.session.commit()
    new_buy = history()
    new_buy.users = username
    new_buy.time = date
    new_buy.code = code
    new_buy.price = price
    new_buy.amount = amount
    new_buy.commission = commission
    new_buy.position = "buy"
    db.session.add(new_buy)
    db.session.commit()
    return jsonify({"result": "success"})


@api_blueprint.route('/sellStock', methods=['GET', 'POST'])
def sellstock():
    username = current_user.username
    date = request.form.get('date')
    code = request.form.get('codeName')
    price = string.atof(request.form.get('price').encode("utf-8"))
    amount = string.atof(request.form.get('amount').encode("utf-8"))
    commission = string.atof(request.form.get('commission').encode("utf-8"))
    result = investment_portfolio.query.filter_by(user_name=current_user.username, code=code).first()
    if (result is None):
        return jsonify({"result": "no stock can be sold"})
    else:
        if (result.shares < amount):
            return jsonify({"result": "not enough stock to be sold"})
        elif (result.shares == amount):
            investment_portfolio.query.filter_by(user_name=current_user.username,
                                                 code=code).delete()  # delete position info of stocks with 0 shares
        result.total_cost = (result.total_cost * result.shares - price * amount * (1 + commission)) / (
            result.shares - amount)  # average cost per share
        result.shares = result.shares - amount
        db.session.commit()
    new_buy = history()
    new_buy.users = username
    new_buy.time = date
    new_buy.code = code
    new_buy.price = price
    new_buy.amount = amount
    new_buy.commission = commission
    new_buy.position = "sell"
    db.session.add(new_buy)
    db.session.commit()
    return jsonify({"result": "success"})


@api_blueprint.route('/analysis/position', methods=['GET', 'POST'])
def position_data():
    data = investment_portfolio.query.filter_by(user_name=current_user.username).all()
    # 用first 结果判断用is not none 用all 判断用[]
    results = []
    if (data != []):
        for result in data:
            results.append({"code": result.code, "num": result.num})
        # return jsonify({"status":"exist","data":results})
        return jsonify(results)
    else:
        return jsonify(results)


@api_blueprint.route('/analysis/history_data', methods=['GET', 'POST'])
def history_data():
    results = []
    data = history.query.filter_by(users=current_user.username).order_by(db.desc(history.time)).all()
    if (data != []):
        for result in data:
            results.append(
                    {"code": result.code, "position": result.position, "price": result.price, "amount": result.amount,
                     "value": result.value, "time": result.time.strftime('%Y-%m-%d')})
        # return jsonify({"status":"exist","data":results})
        return jsonify(results)
    else:
        return jsonify(results)


@api_blueprint.route('/clearall', methods=['GET', 'POST'])
def clearall():
    data = db.session.query(history).filter(history.users == current_user.username).delete(synchronize_session=False)
    db.session.commit()
    data = db.session.query(investment_portfolio).filter(
            investment_portfolio.user_name == current_user.username).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({"result": "success"})


# data format {"date":[],"profit":[],"cost":[],"value":[]}
# value refers to the market value
@api_blueprint.route('/positionhistory', methods=['GET', 'POST'])
def positionhistory():
    username = request.args.get('username')
    data = history.query.filter_by(users=username).order_by(db.desc(history.time)).all()
    getdata = Profit_monitoring(data)
    results = getdata.start()
    # get trade records
    trade_records = history.query.filter_by(users=username).all()
    namelist = []
    for i in range(len(trade_records)):
        stock_name = stock_basics.query.filter_by(trade_code=trade_records[i].code).first().sec_name
        namelist.append(stock_name)
    t_records = []
    for i in range(len(trade_records)):
        record = [trade_records[i].code, namelist[i], trade_records[i].position, trade_records[i].price,
                  trade_records[i].amount, trade_records[i].time.strftime('%Y-%m-%d')]
        t_records.append(record)
    res = {
        'results': results,
        'traderec': t_records,
    }
    return jsonify(res)


@api_blueprint.route('/home/stats', methods=['GET', 'POST'])
def home():
    username = request.args.get('username')
    permission_id = users_roles.query.filter_by(user_name=username).first().permissions
    rolename = Role.query.filter_by(id=permission_id).first().description
    favorite_stock_count = favorite_code.query.filter_by(user_name=username).count()
    position_stock_count = investment_portfolio.query.filter_by(user_name=username).count()
    trade_rec_count = history.query.filter_by(users=username).count()
    position_records = investment_portfolio.query.filter_by(user_name=username).all()
    pricelist = []
    for i in range(len(position_records)):
        pri = string.atof(ts.get_realtime_quotes(position_records[i].code).pre_close[0].encode("utf-8"))
        pricelist.append(pri)
    p_records = []
    for i in range(len(position_records)):
        rec = (pricelist[i] - position_records[i].total_cost) * position_records[i].shares
        p_records.append(rec)
    position_profit = sum(p_records)
    # get city info. return a dictionary {cityname:count}
    citycount = {}
    for i in range(len(position_records)):
        city = stock_basics.query.filter_by(trade_code=position_records[i].code).first().city
        if (citycount.has_key(city)):
            citycount[city] += 1
        else:
            citycount[city] = 1
    cityrec = []
    for key in citycount:
        rec = [key, citycount[key]]
        cityrec.append(rec)

    results = {
        'rolename': rolename,
        'favorite_stock_count': favorite_stock_count,
        'position_stock_count': position_stock_count,
        'trade_rec_count': trade_rec_count,
        'position_profit': position_profit,
        'cityrec': cityrec,
    }
    return jsonify(results)


@api_blueprint.route('/myposition', methods=['GET', 'POST'])
def myposition():
    username = request.args.get('username')
    # get trade records
    trade_records = history.query.filter_by(users=username).all()
    namelist = []
    for i in range(len(trade_records)):
        stock_name = stock_basics.query.filter_by(trade_code=trade_records[i].code).first().sec_name
        namelist.append(stock_name)
    t_records = []
    for i in range(len(trade_records)):
        record = [trade_records[i].code, namelist[i], trade_records[i].position, trade_records[i].price,
                  trade_records[i].amount, trade_records[i].time.strftime('%Y-%m-%d')]
        t_records.append(record)
    # get commission records
    c_records = []
    for i in range(len(trade_records)):
        record = [trade_records[i].code, namelist[i], trade_records[i].commission, trade_records[i].amount]
        c_records.append(record)
    # get position records
    position_records = investment_portfolio.query.filter_by(user_name=username).all()
    namelist = []
    for i in range(len(position_records)):
        stock_name = stock_basics.query.filter_by(trade_code=position_records[i].code).first().sec_name
        namelist.append(stock_name)
    # get latest closing price
    pricelist = []
    for i in range(len(position_records)):
        pri = string.atof(ts.get_realtime_quotes(position_records[i].code).pre_close[0].encode("utf-8"))
        pricelist.append(pri)
    p_records = []
    for i in range(len(position_records)):
        rec = [position_records[i].code, namelist[i], position_records[i].shares, position_records[i].total_cost,
               pricelist[i], (pricelist[i] - position_records[i].total_cost) * position_records[i].shares]
        p_records.append(rec)
    # get department info
    departmentlist = []
    for i in range(len(position_records)):
        dep = stock_basics.query.filter_by(trade_code=position_records[i].code).first().industry_gics
        departmentlist.append(dep)
    d_records = []
    for i in range(len(position_records)):
        rec = [namelist[i], departmentlist[i]]
        d_records.append(rec)

    # get group info
    grouplist = []
    for i in range(len(position_records)):
        gro = basic_stock.query.filter_by(code=position_records[i].code).first().industry
        grouplist.append(gro)
    g_records = []
    for i in range(len(position_records)):
        rec = [namelist[i], grouplist[i]]
        g_records.append(rec)

    # get city info. return a dictionary {cityname:count}
    citycount = {}
    for i in range(len(position_records)):
        city = stock_basics.query.filter_by(trade_code=position_records[i].code).first().city
        if (citycount.has_key(city)):
            citycount[city] += 1
        else:
            citycount[city] = 1
    cityrec = []
    for key in citycount:
        rec = [key, citycount[key]]
        cityrec.append(rec)
    # get group info
    g_records = []
    for i in range(len(position_records)):
        rec = [namelist[i], grouplist[i]]
        g_records.append(rec)

    results = {
        'traderec': t_records,
        'positionrec': p_records,
        'commissionrec': c_records,
        'departmentrec': d_records,
        'grouprec': g_records,
        'cityrec': cityrec,
    }
    return jsonify(results)


@api_blueprint.route('/stock_solo/stock_basic', methods=['GET', 'POST'])
def stock_solo():
    stockcode = request.args.get('code')
    df = ts.get_realtime_quotes(stockcode)  # Single stock symbol
    price = df.price[0]
    rate = string.atof(df.price[0].encode("utf-8")) / string.atof(df.pre_close[0].encode("utf-8"))
    data = favorite_code.query.filter_by(code=stockcode).all()
    count = len(data)
    return jsonify({"price": price, "roc": rate, "count": count})


@api_blueprint.route('/stock_solo/stock_k', methods=['GET', 'POST'])
def stock_solo_k():
    stockcode = request.args.get('code')
    period = request.args.get('period')
    now = datetime.now()
    delta = timedelta(days=string.atoi(period.encode("utf-8")))
    n_days = now - delta
    starttime = n_days.strftime('%Y-%m-%d')
    results = []
    df_deal = pd.DataFrame()
    df = ts.get_hist_data(stockcode, starttime)  # Single stock symbol
    df = df.sort_index(ascending=True)
    date = df.index.tolist()
    df_deal['open'] = df.open
    df_deal['close'] = df.close
    df_deal['low'] = df.low
    df_deal['high'] = df.high
    ma5 = df.ma5.tolist()
    ma10 = df.ma10.tolist()
    ma20 = df.ma20.tolist()
    p_change = df.p_change.tolist()
    for indexs in df_deal.index:
        mylist = (df_deal.loc[indexs].values.tolist())
        mylist.append(indexs)
        results.append(mylist)
    return jsonify({"date": date, "k_data": results, "ma5": ma5, "ma10": ma10, "ma20": ma20, "p_change": p_change})
