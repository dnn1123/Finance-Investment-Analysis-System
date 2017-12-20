# encoding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify, flash
from webapp.models import *
import MySQLdb, time, re
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me
from flask_login import current_user
import string
import tushare as ts
import gc
from  webapp.stratlib import *
api_blueprint = Blueprint(
        'restfulapi',
        __name__,
        url_prefix='/api'
)


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
                       func.sum(finance_basics_add.net_assets).label("net_assets"),
                       func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                       func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                       func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                       func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                       func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                       func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                       finance_basics_add.the_year.label("the_year")).group_by(finance_basics_add.the_year).all()
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
    data['value']='success'
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
    results = favorite_code.query.filter_by(user_name=user_name).all()
    for result in results:
        code_list.append(result.code)
        result1 = finance_basics.query.filter_by(trade_code=result.code).first_or_404()
        name_list.append(result1.sec_name)
    data['code_list'] = code_list
    data['name_list'] = name_list
    data['user_name'] = current_user.username
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
    username=current_user.username
    date=request.form.get('date')
    code=request.form.get('codeName')
    price=string.atof(request.form.get('price').encode("utf-8"))
    amount=string.atof(request.form.get('amount').encode("utf-8"))
    commission=string.atof(request.form.get('commission').encode("utf-8"))
    result = investment_portfolio.query.filter_by(user_name=current_user.username, code=code).first()
    if (result is None):
        new_data = investment_portfolio()
        new_data.user_name = current_user.username
        new_data.code = code
        new_data.shares = amount
        new_data.total_cost = price * amount * (1 + commission) / amount #average cost per share
        db.session.add(new_data)
        db.session.commit()
    else:
        result.total_cost = (result.total_cost * result.shares + price * amount * (1 + commission))/(result.shares+ amount)#average cost per share
        result.shares = result.shares + amount
        db.session.commit()
    new_buy=history()
    new_buy.users=username
    new_buy.time=date
    new_buy.code=code
    new_buy.price=price
    new_buy.amount=amount
    new_buy.commission=commission
    new_buy.position="buy"
    db.session.add(new_buy)
    db.session.commit()
    return jsonify({"result":"success"})

@api_blueprint.route('/sellStock', methods=['GET', 'POST'])
def sellstock():
    username=current_user.username
    date=request.form.get('date')
    code=request.form.get('codeName')
    price=string.atof(request.form.get('price').encode("utf-8"))
    amount=string.atof(request.form.get('amount').encode("utf-8"))
    commission=string.atof(request.form.get('commission').encode("utf-8"))
    result = investment_portfolio.query.filter_by(user_name=current_user.username, code=code).first()
    if (result is None):
        return jsonify({"result":"no stock can be sold"})
    else:
        if(result.shares < amount):
            return jsonify({"result":"not enough stock to be sold"})
        elif (result.shares == amount):
            investment_portfolio.query.filter_by(user_name=current_user.username, code=code).delete() # delete position info of stocks with 0 shares
        result.total_cost = (result.total_cost * result.shares - price * amount * (1 + commission))/(result.shares- amount)#average cost per share
        result.shares = result.shares - amount
        db.session.commit()
    new_buy=history()
    new_buy.users=username
    new_buy.time=date
    new_buy.code=code
    new_buy.price=price
    new_buy.amount=amount
    new_buy.commission=commission
    new_buy.position="sell"
    db.session.add(new_buy)
    db.session.commit()
    return jsonify({"result":"success"})

@api_blueprint.route('/analysis/position', methods=['GET', 'POST'])
def position_data():
    data=investment_portfolio.query.filter_by(user_name=current_user.username).all()
    # 用first 结果判断用is not none 用all 判断用[]
    results=[]
    if (data != []):
        for result in data:
            results.append({"code":result.code,"num":result.num})
        # return jsonify({"status":"exist","data":results})
        return jsonify(results)
    else:
        return jsonify(results)



@api_blueprint.route('/analysis/history_data', methods=['GET', 'POST'])
def history_data():
    results=[]
    data=history.query.filter_by(users=current_user.username).order_by(db.desc(history.time)).all()
    if (data != []):
        for result in data:
            results.append({"code":result.code,"position":result.position,"price":result.price,"amount":result.amount,"value":result.value,"time":result.time.strftime('%Y-%m-%d')})
        # return jsonify({"status":"exist","data":results})
        return jsonify(results)
    else:
        return jsonify(results)


@api_blueprint.route('/clearall', methods=['GET', 'POST'])
def clearall():
    data = db.session.query(history).filter(history.users==current_user.username).delete(synchronize_session=False)
    db.session.commit()
    data = db.session.query(investment_portfolio).filter(investment_portfolio.user_name==current_user.username).delete(synchronize_session=False)
    db.session.commit()
    return jsonify({"result": "success"})

# data format {"date":[],"profit":[],"cost":[],"value":[]}
# value refers to the market value
@api_blueprint.route('/positionhistory', methods=['GET', 'POST'])
def positionhistory():
    username = request.args.get('username')
    data = history.query.filter_by(users=username).order_by(db.desc(history.time)).all()
    getdata=Profit_monitoring(data)
    results=getdata.start()
    print results
    return jsonify(results)

@api_blueprint.route('/home/stats',methods=['GET','POST'])
def home():
    username = request.args.get('username')
    permission_id = users_roles.query.filter_by(user_name = username).first().permissions
    rolename = Role.query.filter_by(id=permission_id).first().description
    favorite_stock_count = favorite_code.query.filter_by(user_name=username).count()
    position_stock_count = investment_portfolio.query.filter_by(user_name=username).count()

    position_records = investment_portfolio.query.filter_by(user_name=username).all()
    pricelist = []
    for i in range(len(position_records)):
        pri = string.atof(ts.get_realtime_quotes(position_records[i].code).pre_close[0].encode("utf-8"))
        pricelist.append(pri)
    p_records=[]
    for i in range(len(position_records)):
        rec = (pricelist[i]-position_records[i].total_cost)*position_records[i].shares
        p_records.append(rec)
    position_profit = sum(p_records)
    results = {
        'rolename':rolename,
        'favorite_stock_count':favorite_stock_count,
        'position_stock_count':position_stock_count,
        'position_profit':position_profit,
    }
    return jsonify(results)
@api_blueprint.route('/myposition',methods=['GET','POST'])
def myposition():
    username=request.args.get('username')
    # get trade records
    trade_records = history.query.filter_by(users=username).all()
    namelist = []
    for i in range(len(trade_records)):
        stock_name = stock_basics.query.filter_by(trade_code=trade_records[i].code).first().sec_name
        namelist.append(stock_name)
    t_records=[]
    for i in range(len(trade_records)):
        record = [trade_records[i].code, namelist[i],trade_records[i].position,trade_records[i].price, trade_records[i].amount, trade_records[i].time]
        t_records.append(record)
    #get commission records
    c_records = []
    for i in range(len(trade_records)):
        record = [trade_records[i].code, namelist[i],trade_records[i].commission, trade_records[i].amount ]
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
    p_records=[]
    for i in range(len(position_records)):
        rec = [position_records[i].code,namelist[i],position_records[i].shares,position_records[i].total_cost,pricelist[i],(pricelist[i]-position_records[i].total_cost)*position_records[i].shares]
        p_records.append(rec)
    #get department info
    departmentlist = []
    for i in range(len(position_records)):
        dep = stock_basics.query.filter_by(trade_code = position_records[i].code).first().industry_gics
        departmentlist.append(dep)
    d_records=[]
    for i in range(len(position_records)):
        rec = [namelist[i],departmentlist[i]]
        d_records.append(rec)
    #get group info
    grouplist = []
    for i in range(len(position_records)):
        gro = basic_stock.query.filter_by(code = position_records[i].code).first().industry
        grouplist.append(gro)
    g_records=[]
    for i in range(len(position_records)):
        rec = [namelist[i],grouplist[i]]
        g_records.append(rec)
    results = {
        'traderec':t_records,
        'positionrec':p_records,
        'commissionrec':c_records,
        'departmentrec':d_records,
        'grouprec':g_records,
    }
    return jsonify(results)

