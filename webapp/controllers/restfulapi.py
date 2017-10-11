#encoding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request,session,make_response,jsonify
from webapp.models import *
import MySQLdb, time, re

api_blueprint = Blueprint(
    'restfulapi',
    __name__,
    url_prefix='/api'
)

@api_blueprint.route("/finance_data/",methods=('GET','POST'))
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
    year_list=[]



    for index in indexes:
        exec(index+"_list=[]")

    for result in results:
        year_list.append (result.the_year)
        for index in indexes:
            if eval("result."+index) is None:
                exec (index + "_list.append(result."+index+")")
            else:
                exec(index+"_list.append(float(result."+index+"))")
    data['stock_code'] = stockcode
    data['the_year'] = year_list
    data['indexes']=indexes
    for index in indexes:
        exec("data['"+index+"']="+index+"_list")
    return jsonify(data)
