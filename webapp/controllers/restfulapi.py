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

    filters = {
        finance_basics_add.the_year >= starttime,
        finance_basics_add.the_year <= endtime,
    }
    results = finance_basics_add.query.filter(*filters).all()

    year_list = []
    for year in years:
        year_list.append(year.the_year)

    for index in indexes:
        exec (index + "_list=[]")
    for index in indexes:
        for y in year_list:
            for result in results:
                if result.the_year == y:
                    if eval("result." + index) is not None:
                        exec ("x += float((result." + index + ")/100000000)")
            exec (index + "_list.append(x)")

    data['the_year'] = year_list
    data['indexes'] = indexes

    for index in indexes:
        exec ("data['" + index + "']=" + index + "_list")
    return jsonify(data)
