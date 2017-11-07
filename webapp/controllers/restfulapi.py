# encoding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify
from webapp.models import *
import MySQLdb, time, re

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
    trade_code = request.form.get('trade_code')
    gics_4 = request.form.get('gics_4')
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    session.query(cns_stock_industry).filter(cns_stock_industry.trade_code == trade_code).update(
        {'belong': gics_4})  # 改为belong
    session.commit()  # 少写了这一行，所以修改没成功
    return redirect(url_for('.home'))