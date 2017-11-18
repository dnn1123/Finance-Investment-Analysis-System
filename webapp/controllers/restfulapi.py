# encoding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify
from webapp.models import *
import MySQLdb, time, re
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me

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
    if(result1):
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

    x = 0

    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    indexes = request.args.getlist('indexes[]')

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

    for y in year_list:
        results = finance_basics_add.query.filter_by(the_year=y).all()
        for result in results:
            for index in indexes:
                if eval("result." + index) is not None:
                    exec ("my" + index + "+= float((result." + index + ")/100000000)")
        for index in indexes:
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

    min = code + '101000'
    max = code + '990000'

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()

    a = {
        cns_stock_industry.industry_gicscode_4 <= max,
        cns_stock_industry.industry_gicscode_4 >= min,
    }
    rs = cns_stock_industry.query.filter(*a).all()

    year_list = []
    for year in years:
        year_list.append(year.the_year)

    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")

    for y in year_list:
        for r in rs:
            result = finance_basics_add.query.filter_by(the_year=y, trade_code=r.trade_code).first_or_404()
            for index in indexes:
                if eval("result." + index) is not None:
                    exec ("my" + index + "+= float((result." + index + ")/100000000)")
        for index in indexes:
            exec (index + "_list.append(my" + index + ")")

    data['the_year'] = year_list
    data['indexes'] = indexes

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

    min = code + '1000'
    max = code + '9900'

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()

    a = {
        cns_stock_industry.industry_gicscode_4 <= max,
        cns_stock_industry.industry_gicscode_4 >= min,
    }
    rs = cns_stock_industry.query.filter(*a).all()

    year_list = []
    for year in years:
        year_list.append(year.the_year)

    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")

    for y in year_list:
        for r in rs:
            result = finance_basics_add.query.filter_by(the_year=y, trade_code=r.trade_code).first_or_404()
            for index in indexes:
                if eval("result." + index) is not None:
                    exec ("my" + index + "+= float((result." + index + ")/100000000)")
        for index in indexes:
            exec (index + "_list.append(my" + index + ")")

    data['the_year'] = year_list
    data['indexes'] = indexes

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

    min = code + '09'
    max = code + '90'

    Filters = {
        finance_basics_add.trade_code == '000002',
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    years = finance_basics_add.query.filter(*Filters).all()

    a = {
        cns_stock_industry.industry_gicscode_4 <= max,
        cns_stock_industry.industry_gicscode_4 >= min,
    }
    rs = cns_stock_industry.query.filter(*a).all()

    year_list = []
    for year in years:
        year_list.append(year.the_year)

    for index in indexes:
        exec (index + "_list=[]")
        exec ("my" + index + "=0")

    for y in year_list:
        i = 0
        for r in rs:
            i = i + 1
            result = finance_basics_add.query.filter_by(the_year=y, trade_code=r.trade_code).first_or_404()
            for index in indexes:
                if eval("result." + index) is not None:
                    exec ("my" + index + "+= float((result." + index + ")/100000000)")
        for index in indexes:
            exec (index + "_list.append(my" + index + ")")

    data['the_year'] = year_list
    data['indexes'] = indexes

    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)

@api_blueprint.route("/stock_code/", methods=('GET', 'POST'))
def stock_code():
    stockcode = request.args.get('q')
    filters = {
        stock_basics.trade_code.like("%"+stockcode+"%")
    }
    results = stock_basics.query.filter(*filters).all()
    data={}
    stockcode_list=[]
    secname_list=[]
    for result in results:
        stockcode_list.append(result.trade_code)
        secname_list.append(result.sec_name)
    data['stockcode']=stockcode_list
    data['stockname']=secname_list
    return jsonify(data)


@api_blueprint.route("/gics_1/", methods=('GET', 'POST'))
def gics_1():
    results = cnsb_department_industry.query.all()
    list=[]
    for result in results:
        list.append({"gicscode1":result.industry_gicscode_1,"gics1":result.industry_gics_1})
    return jsonify(list)
@api_blueprint.route("/gics_2/", methods=('GET', 'POST'))
def gics_2():
    code=request.args.get("code")
    filters = {
        cnsb_group_industry.belong == code
    }
    results = cnsb_group_industry.query.filter(*filters).all()
    list=[]
    for result in results:
        list.append({"gicscode2":result.industry_gicscode_2,"gics2":result.industry_gics_2})
    return jsonify(list)

@api_blueprint.route("/gics_3/", methods=('GET', 'POST'))
def gics_3():
    code=request.args.get("code")
    filters = {
        cnsb_industry.belong == code
    }
    results = cnsb_industry.query.filter(*filters).all()
    list=[]
    for result in results:
        list.append({"gicscode3":result.industry_gicscode_3,"gics3":result.industry_gics_3})
    return jsonify(list)

@api_blueprint.route("/gics_4/", methods=('GET', 'POST'))
def gics_4():
    code=request.args.get("code")
    filters = {
        cnsb_sub_industry.belong == code
    }
    results = cnsb_sub_industry.query.filter(*filters).all()
    list=[]
    for result in results:
        list.append({"gicscode4":result.industry_gicscode_4,"gics4":result.industry_gics_4})
    return jsonify(list)

@api_blueprint.route("/update_gics/", methods=('GET', 'POST'))
def update_gics():
    trade_code = request.values.get("trade_code")
    gics_4 = request.values.get('gics_4')
    gics_name=request.values.get('gics_name')
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    session.query(cns_stock_industry).filter(cns_stock_industry.trade_code == trade_code).update(
        {'belong': gics_4,'industry_gicscode_4':gics_4,'industry_gics_4':gics_name})  # 改为belong
    session.commit()  # 少写了这一行，所以修改没成功
    return "true"
@api_blueprint.route("/update_gicsb/", methods=('GET', 'POST'))
def update_gicsb():
    trade_code = request.values.get("trade_code")
    gics_4 = request.values.get('gics_4')
    gics_name=request.values.get('gics_name')
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    session.query(cnsb_stock_industry).filter(cnsb_stock_industry.trade_code == trade_code).update(
        {'industry_gicscode_4':gics_4,'industry_gics_4':gics_name})  # 改为belong
    session.commit()  # 少写了这一行，所以修改没成功
    return "true"