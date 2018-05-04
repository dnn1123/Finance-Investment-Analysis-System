# encoding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify, flash
from webapp.models import *
import MySQLdb, time, re
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me

industry_analysis_api = Blueprint(
    'industry_analysis_api',
    __name__,
    url_prefix="/industry_analysis_api"
)

@industry_analysis_api.route("/market_value/", methods=('GET', 'POST'))
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

@industry_analysis_api.route("/market_one/", methods=('GET', 'POST'))
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
        results = stock_basics.query.filter(*filters).all()
    code_list = []
    for result in results:
        code_list.append(result.trade_code)
    # yc_end
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    data_list = []
    for index in indexes:
        exec (index + "_list=[]")
    for code in codes:
        results = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                                func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                                func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                                func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                                cns_department_industry.industry_gics_1.label("industry_gics_1")).filter(
            finance_basics_add.the_year == time).filter(
            finance_basics_add.trade_code.in_(code_list)).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
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

                exec (index + "_list.append(my" + index + ")")
    data = {}
    for index in indexes:
        exec ("data['" + index + "_list']=" + index + "_list")
    data['my_code'] = codes
    data['province'] = province

    return jsonify(data)


@industry_analysis_api.route("/market_status1/", methods=('GET', 'POST'))
def market_status1():
    data = {}
    code = request.args.get('code')
    province = request.args.get('province')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')
    # yc
    if province == 'all':
        results = stock_basics.query.filter().all()
    else:
        filters = {
            stock_basics.province.like("%" + province + "%")
        }
        results = stock_basics.query.filter(*filters).all()
    code_list = []
    for result in results:
        code_list.append(result.trade_code)
    # yc_end
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
                       func.sum(finance_basics_add.net_assets).label("net_assets"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                       cns_department_industry.industry_gics_1.label("industry_gics_1")).filter(
        finance_basics_add.trade_code.in_(code_list)).filter(
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


@industry_analysis_api.route("/market_status2/", methods=('GET', 'POST'))
def market_status2():
    data = {}
    province = request.args.get('province')
    code = request.args.get('code')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')
    # yc
    if province == 'all':
        results = stock_basics.query.filter().all()
    else:
        filters = {
            stock_basics.province.like("%" + province + "%")
        }
        results = stock_basics.query.filter(*filters).all()
    code_list = []
    for result in results:
        code_list.append(result.trade_code)
    # yc_end
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
                       func.sum(finance_basics_add.net_assets).label("net_assets"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                       cns_group_industry.industry_gics_2.label("industry_gics_2")).filter(
        finance_basics_add.trade_code.in_(code_list)).filter(
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


@industry_analysis_api.route("/market_status3/", methods=('GET', 'POST'))
def market_status3():
    data = {}
    province = request.args.get('province')
    code = request.args.get('code')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')
    # yc
    if province == 'all':
        results = stock_basics.query.filter().all()
    else:
        filters = {
            stock_basics.province.like("%" + province + "%")
        }
        results = stock_basics.query.filter(*filters).all()
    code_list = []
    for result in results:
        code_list.append(result.trade_code)
    # yc_end
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
                       func.sum(finance_basics_add.net_assets).label("net_assets"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                       cns_industry.industry_gics_3.label("industry_gics_3")).filter(
        finance_basics_add.trade_code.in_(code_list)).filter(
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


@industry_analysis_api.route("/market_status4/", methods=('GET', 'POST'))
def market_status4():
    data = {}
    province = request.args.get('province')
    code = request.args.get('code')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')
    # yc
    if province == 'all':
        results = stock_basics.query.filter().all()
    else:
        filters = {
            stock_basics.province.like("%" + province + "%")
        }
        results = stock_basics.query.filter(*filters).all()
    code_list = []
    for result in results:
        code_list.append(result.trade_code)
    # yc_end
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
                       func.sum(finance_basics_add.net_assets).label("net_assets"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                       cns_sub_industry.industry_gicscode_4,
                       cns_sub_industry.industry_gics_4.label("industry_gics_4")).filter(
        finance_basics_add.trade_code.in_(code_list)).filter(
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


@industry_analysis_api.route("/market_bumen/", methods=('GET', 'POST'))
def market_bumen():
    data = {}
    value = []
    index = []

    results = cnsb_department_industry.query.all()

    for result in results:
        value.append(result.industry_gicscode_1)
        index.append(result.industry_gics_1)

    data['my_value'] = value
    data['my_index'] = index

    return jsonify(data)

@industry_analysis_api.route("/market_hangyezu/", methods=('GET', 'POST'))
def market_hangyezu():
    data = {}
    value = []
    index = []

    results = cns_group_industry.query.all()

    for result in results:
        value.append(result.industry_gicscode_2)
        index.append(result.industry_gics_2)

    data['my_value'] = value
    data['my_index'] = index

    return jsonify(data)


@industry_analysis_api.route("/market_hangye/", methods=('GET', 'POST'))
def market_hangye():
    data = {}
    value = []
    index = []

    results = cnsb_industry.query.all()

    for result in results:
        value.append(result.industry_gicscode_3)
        index.append(result.industry_gics_3)

    data['my_value'] = value
    data['my_index'] = index

    return jsonify(data)


@industry_analysis_api.route("/market_zihangye/", methods=('GET', 'POST'))
def market_zihangye():
    data = {}
    value = []
    index = []

    results = hks_sub_industry.query.all()

    for result in results:
        value.append(result.industry_gicscode_4)
        index.append(result.industry_gics_4)

    data['my_value'] = value
    data['my_index'] = index

    return jsonify(data)


@industry_analysis_api.route("/market_form1/", methods=('GET', 'POST'))
def market_form1():
    data = {}
    value = []
    index = []

    code = request.args.get('code')

    Filters = {
        cns_group_industry.belong == code,
    }
    results = cns_group_industry.query.filter(*Filters).all()

    for result in results:
        value.append(result.industry_gicscode_2)
        index.append(result.industry_gics_2)

    data['my_value'] = value
    data['my_index'] = index

    return jsonify(data)


@industry_analysis_api.route("/market_form2/", methods=('GET', 'POST'))
def market_form2():
    data = {}
    value = []
    index = []

    code = request.args.get('code')

    Filters = {
        cns_industry.belong == code,
    }
    results = cns_industry.query.filter(*Filters).all()

    for result in results:
        value.append(result.industry_gicscode_3)
        index.append(result.industry_gics_3)

    data['my_value'] = value
    data['my_index'] = index

    return jsonify(data)


@industry_analysis_api.route("/market_form3/", methods=('GET', 'POST'))
def market_form3():
    data = {}
    value = []
    index = []

    code = request.args.get('code')

    Filters = {
        cns_sub_industry.belong == code,
    }
    results = cns_sub_industry.query.filter(*Filters).all()

    for result in results:
        value.append(result.industry_gicscode_4)
        index.append(result.industry_gics_4)

    data['my_value'] = value
    data['my_index'] = index

    return jsonify(data)

