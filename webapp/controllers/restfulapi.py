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
from webapp.Library.wind_mysql.get_company_list import *

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
        'name_list': name_list,
        "permission_list": permission_list
    }
    return jsonify(data)


# 购买数据
@api_blueprint.route('/ buy_data', methods=['GET', 'POST'])
def buy_data():
    username = request.args.get('username')

    money = user_money.query.filter_by(user_name=username).first_or_404().user_money
    member_type = member_information.query.filter_by(user_name=username).first_or_404().member_type
    time = member_information.query.filter_by(user_name=username).first_or_404().member_expiration_date
    results = {
        'user_money': money,
        'member_type': member_type,

    }
    return jsonify(results)


# 账户余额操作，充值，花费
@api_blueprint.route('/change_money', methods=['GET', 'POST'])
def change_money():
    username = current_user.username
    action =  request.args.get('action')
    count = request.args.get('count')

    if(action == 'sub'):
        result = user_money.query.filter_by(user_name=username).first_or_404()
        result.user_money = result.user_money - int(count)
        db.session.commit()
    else:
        result = user_money.query.filter_by(user_name=username).first_or_404()
        result.user_money = result.user_money + int(count)
        db.session.commit()
    results = {
        'action':action,
        'count':count,

    }
    return jsonify(results)






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


@api_blueprint.route('/change_permission', methods=('GET', 'POST'))
def change_permission():
    name = request.form.get('name')
    permission = request.form.get('permission')

    old_users_roles = users_roles.query.filter_by(user_name=name).first()
    db.session.delete(old_users_roles)
    db.session.commit()

    n_users_roles = users_roles(user_name=name)
    n_users_roles.permissions = permission
    db.session.add(n_users_roles)
    db.session.commit()
    data = {
        'name': name,
        'permission': permission
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
    for i in range(0,len(results['profit'])):
        results['profit'][i] = round(results['profit'][i],4)
        results['cost'][i] = round(results['cost'][i],4)
        results['value'][i] = round(results['value'][i],4)
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
    money = user_money.query.filter_by(user_name=username).first_or_404().user_money
    member_type = member_information.query.filter_by(user_name=username).first_or_404().member_type
    time = member_information.query.filter_by(user_name=username).first_or_404().member_expiration_date
    results = {
        'rolename': rolename,
        'favorite_stock_count': favorite_stock_count,
        'position_stock_count': position_stock_count,
        'trade_rec_count': trade_rec_count,
        'position_profit': position_profit,
        'cityrec': cityrec,
        'user_money': money,
        'member_type': member_type,
        'time': time,
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


@api_blueprint.route('/stock_group/cns_home', methods=['GET', 'POST'])
def cns_home():
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    pie1 = db.session.query(cns_department_industry.industry_gics_1, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_department_industry.industry_gicscode_1).all()
    pie2 = db.session.query(cns_group_industry.industry_gics_2, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_group_industry.industry_gicscode_2).all()

    pie3 = db.session.query(cns_industry.industry_gics_3, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_industry.industry_gicscode_3).all()

    pie4 = db.session.query(cns_sub_industry.industry_gics_4, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_sub_industry.industry_gicscode_4).all()
    for i in pie1:
        pie1_data.append({'name': i[0], 'value': i[1]})
    for i in pie2:
        pie2_data.append({'name': i[0], 'value': i[1]})
    for i in pie3:
        pie3_data.append({'name': i[0], 'value': i[1]})
    for i in pie4:
        pie4_data.append({'name': i[0], 'value': i[1]})
    return jsonify({"pie1", pie1_data})

@api_blueprint.route('/updata_company_list', methods=['GET', 'POST'])
def updata_company_list():
    data={}
    # upData_company_list()
    # upData_cns_stock_basics()
    # data = upData_cns_balance_sheet()
    return jsonify(data)

# 获取数据库中所有财务指标
@api_blueprint.route("/finance_target/", methods=('GET', 'POST'))
def finance_target():
    results1 = cns_financial_target_1.query.all()
    results2 = cns_financial_target_2.query.all()
    results3 = cns_financial_target_3.query.all()
    results4 = cns_financial_target_4.query.all()

    data = {}
    id_list = []
    cn_name_list = []
    en_name_list = []
    id_belong_to_list = []
    for result1 in results1:
        id_list.append(result1.id_1)
        cn_name_list.append(result1.cn_name_1)
        en_name_list.append(result1.en_name_1)
        id_belong_to_list.append('-1')
        for result2 in results2:
            if result2.id_belong_to_1 == result1.id_1:
                id_list.append(result2.id_2)
                cn_name_list.append(result2.cn_name_2)
                en_name_list.append(result2.en_name_2)
                id_belong_to_list.append(result2.id_belong_to_1)
                for result3 in results3:
                    if result3.id_belong_to_2 == result2.id_2:
                        id_list.append(result3.id_3)
                        cn_name_list.append(result3.cn_name_3)
                        en_name_list.append(result3.en_name_3)
                        id_belong_to_list.append(result3.id_belong_to_2)
                        for result4 in results4:
                            if result4.id_belong_to_3 == result3.id_3:
                                id_list.append(result4.id_4)
                                cn_name_list.append(result4.cn_name_4)
                                en_name_list.append(result4.en_name_4)
                                id_belong_to_list.append(result4.id_belong_to_3)

    data['id'] = id_list
    data['cn_name'] = cn_name_list
    data['en_name'] = en_name_list
    data['id_belong_to'] = id_belong_to_list
    return jsonify(data)


# 新数据库中根据指标获取数据
@api_blueprint.route("/finance_index_data/", methods=('GET', 'POST'))
def finance_index_data():
    stockcode = request.args.get('stockcode')
    starttime = request.args.get('starttime')
    endtime = request.args.get('endtime')
    id = request.args.getlist('id_list[]')
    cn_name_list = request.args.getlist('cn_name_list[]')
    en_name_list = request.args.getlist('en_name_list[]')
    print id
    print en_name_list
    print cn_name_list
    filters_cns_balance_sheet = {
        cns_balance_sheet.stock_code == stockcode,
        cns_balance_sheet.the_date >= starttime,
        cns_balance_sheet.the_date <= endtime,
    }
    results_cns_balance_sheet = cns_balance_sheet.query.filter(*filters_cns_balance_sheet).order_by(db.asc( cns_balance_sheet.the_date)).all()
   # 获取当前股票名称
    results_cns_balance_sheet_name = cns_balance_sheet.query.filter_by(stock_code=stockcode).first_or_404()
    filters_cns_income_statement = {
        cns_income_statement.stock_code == stockcode,
        cns_income_statement.the_date >= starttime,
        cns_income_statement.the_date <= endtime,
    }
    results_cns_income_statement = cns_income_statement.query.filter(*filters_cns_income_statement).order_by(db.asc(cns_income_statement.the_date)).all()
    filters_cns_statement_of_cash_flows = {
        cns_statement_of_cash_flows.stock_code == stockcode,
        cns_statement_of_cash_flows.the_date >= starttime,
        cns_statement_of_cash_flows.the_date <= endtime,
    }
    results_cns_statement_of_cash_flows = cns_statement_of_cash_flows.query.filter(
        *filters_cns_statement_of_cash_flows).order_by(db.asc(cns_statement_of_cash_flows.the_date)).all()
    data = {}
    year_list = []
    indexes = []

    start_year = eval(starttime[0:4])
    start_M = starttime[5:7]
    end_year = eval(endtime[0:4])
    end_M = endtime[5:7]


    if start_M < '04':
        start_Q = 1
    elif start_M < '07':
        start_Q = 2
    elif start_M < '10':
        start_Q = 3
    elif start_M < '13':
        start_Q = 4

    if end_M < '04':
        end_Q = 1
    elif end_M < '07':
        end_Q = 2
    elif end_M < '10':
        end_Q = 3
    elif end_M < '13':
        end_Q = 4

    for i in range(start_Q, 5):
        year_list.append(str(start_year) + "年Q" + str(i))
    if (end_year - start_year) > 1:
        for i in range(start_year + 1, end_year):
            for j in range(1, 5):
                year_list.append(str(i) + "年Q" + str(j))
    for i in range(1, end_Q + 1):
        year_list.append(str(end_year) + "年Q" + str(i))

    for i in range(0, len(id)):

     if id[i][0:2] == "01":
        print id[i]
        if hasattr(cns_balance_sheet, en_name_list[i]):
            temp_list = []
            exec (en_name_list[i] + "_list=[]")
            for result in results_cns_balance_sheet:
                if eval("result." + en_name_list[i]) is None:
                    exec ("temp_list.append(result." + en_name_list[i] + ")")
                else:
                    exec ("temp_list.append(float(result." + en_name_list[i] + "))")
            data[en_name_list[i] + "_list"] = temp_list
            data[en_name_list[i]] = cn_name_list[i]
            indexes.append(en_name_list[i])
     elif id[i][0:2] == "02":
        print id[i]
        if hasattr(cns_income_statement, en_name_list[i]):
            temp_list = []
            exec (en_name_list[i] + "_list=[]")
            for result in results_cns_income_statement:
                if eval("result." + en_name_list[i]) is None:
                    exec ("temp_list.append(result." + en_name_list[i] + ")")
                else:
                    exec ("temp_list.append(float(result." + en_name_list[i] + "))")
            data[en_name_list[i] + "_list"] = temp_list
            data[en_name_list[i]] = cn_name_list[i]
            indexes.append(en_name_list[i])
     elif id[i][0:2] == "03":
        print id[i]
        if hasattr(cns_statement_of_cash_flows, en_name_list[i]):
            temp_list = []
            exec (en_name_list[i] + "_list=[]")
            for result in results_cns_statement_of_cash_flows:
                if eval("result." + en_name_list[i]) is None:
                    exec ("temp_list.append(result." + en_name_list[i] + ")")
                else:
                    exec ("temp_list.append(float(result." + en_name_list[i] + "))")
            data[en_name_list[i] + "_list"] = temp_list
            data[en_name_list[i]] = cn_name_list[i]
            indexes.append(en_name_list[i])
    data['the_name'] = results_cns_balance_sheet_name.sec_name
    data['stock_code'] = stockcode
    data['the_year'] = year_list
    data['indexes'] = indexes
    data['id'] = id
    return jsonify(data)