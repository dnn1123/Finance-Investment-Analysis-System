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
    codelist = request.form.getlist('code_list[]')
    date = request.form.getlist('date[]')
    indexes = request.form.getlist('index[]')
    the_year_start = int(date[0][0:4] + '1231')
    the_year_end = int(date[1][0:4] + '1231')
    data = {}
    test = {}
    year_list = []
    year_list1 = []
    the_year = the_year_end
    while the_year >= the_year_start:
        year_list.append(the_year)
        year_list1.append(the_year / 10000)
        the_year = the_year - 10000
    for code in codelist:
        result1 = finance_basics.query.filter_by(trade_code=code).first_or_404()
        test['name'] = result1.sec_name
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
        test[index] = results
        data[code] = test
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
                    results.append('..')
                else:
                    results.append(str(eval('result.' + index)))

        data[index] = results
    data['indexs'] = indexes
    data['the_code'] = code
    data['the_year_list'] = year_list1
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
