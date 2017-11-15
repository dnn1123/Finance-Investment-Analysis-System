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
