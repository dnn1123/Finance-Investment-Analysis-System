# coding=utf-8
from flask import Blueprint,request,render_template,jsonify
from flask_login import current_user
from .bpm import handle_form,handle_liveform,dict_to_sql,sql_to_dict,Strategy_Manager,Strategy,create_position_records,get_stock_list,get_fiducial_value_data
from webapp.stratlib import Profit_monitoring
from webapp.models import strategy,subscriber,db,stock_basics,basic_stock
from webapp.config import paths
import os,datetime,string
import tushare as ts
from time import sleep
quant_api = Blueprint(
    'quant_api',
    __name__,
    template_folder=os.path.abspath(os.path.join(paths.project_path,'Template','quant')),
    url_prefix="/quant_api"
)

#选择策略类型
@quant_api.route('/backtest_form', methods=('GET', 'POST'))
def request_form():
    type=request.args.get('type')
    if type=="Pair_Strategy_Based_Bank":
        return render_template('/form/form_Pair_Strategy_Based_Bank.html')
    if type=="DoubleMA_Strategy":
        return render_template('/form/form_DoubleMA_Strategy.html')
    if type=="My_Pair_Strategy":
        return render_template('/form/form_My_Pair_Strategy.html')
    if type=="Stock_Picking_Strategy_Based_Value_By_Steve_A":
        return render_template('/form/form_Stock_Picking_Strategy_Based_Value_By_Steve_A.html')

#回测
@quant_api.route('/backtest', methods=('GET', 'POST'))
def back_test():
    data,history,Portfolio_data=handle_form(request.form)
    #position history
    namelist = []
    for i in range(len(history)):
        stock_name = stock_basics.query.filter_by(trade_code=history[i].code).first().sec_name
        namelist.append(stock_name)
    t_records = []
    for i in range(len(history)):
        record = [history[i].code, namelist[i], history[i].position, history[i].price,
                  history[i].amount, history[i].time.strftime('%Y-%m-%d')]
        t_records.append(record)
    c_records = []
    for i in range(len(history)):
        record = [history[i].code, namelist[i], history[i].commission, history[i].amount]
        c_records.append(record)
    # get position records
    position_records = create_position_records(history)
    namelist = []
    for i in range(len(position_records)):
        stock_name = stock_basics.query.filter_by(trade_code=position_records[i].code).first().sec_name
        namelist.append(stock_name)
    # get latest closing price
    pricelist = []
    for i in range(len(position_records)):
        pri = ts.get_k_data(position_records[i].code,start=(datetime.datetime.strptime(request.form.get('edate'), "%Y-%m-%d")+datetime.timedelta(days=-30)).strftime("%Y-%m-%d"),end=request.form.get('edate')).iloc[-1:].close
        pricelist.append(pri.values[0])
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
    #绘图数据
    plotter_date=Portfolio_data['date']
    stock_list=get_stock_list(request.form)
    plotter_data=get_fiducial_value_data(string.atof(request.form.get('cash').encode('utf-8')),plotter_date,stock_list,string.atof(request.form.get('commission').encode('utf-8')))
    # plotter_data=[]
    res = {
        'date': [i.strftime("%Y-%m-%d")   for i in plotter_date],
        'traderec': t_records,
        'portfolio':Portfolio_data['data'],
        'compare':plotter_data
    }
    results_all = {
        'data':data,
        'res':res,
        'traderec': t_records,
        'positionrec': p_records,
        'commissionrec': c_records,
        'departmentrec': d_records,
        'grouprec': g_records,
        'cityrec': cityrec,
    }
    return jsonify(results_all)

@quant_api.route('/realtime_form', methods=('GET', 'POST'))
def request_liveform():
    type=request.args.get('type')
    if type=="Pair_Strategy_Based_Bank":
        return render_template('/form/liveform_Pair_Strategy_Based_Bank.html')
    if type=="DoubleMA_Strategy":
        return render_template('/form/liveform_DoubleMA_Strategy.html')
    if type=="My_Pair_Strategy":
        return render_template('/form/liveform_My_Pair_Strategy.html')
    if type=="Buy_Everyday":
        return render_template('form/liveform_Buy_Everyday.html')

@quant_api.route('/subscribe',methods=('GET', 'POST'))
def subscribe():
    data=handle_liveform(request.form)
    new_sub=subscriber()
    new_sub.user=current_user.username
    new_sub.strategy_id=data['strategy_id']
    new_sub.strategy_name=data['strategy_name']
    new_sub.parameter=dict_to_sql(data['params'])
    new_sub.build_date=data['build_date']
    new_sub.status="运行中"
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({"data":"success"})

@quant_api.route('/delete_subscribe',methods=('GET', 'POST'))
def delete_subscribe():
    id=request.args.get('id')
    data=subscriber.query.filter_by(identifier=id).first()
    db.session.delete(data)
    db.session.commit()
    return jsonify({"result":"success"})

@quant_api.route('/stop_subscribe',methods=('GET', 'POST'))
def stop_subscribe():
    id=request.args.get('id')
    data=subscriber.query.filter_by(identifier=id).update({"status":"已停止"})
    db.session.commit()
    return jsonify({"result":"success"})

@quant_api.route('/start_subscribe',methods=('GET', 'POST'))
def start_subscribe():
    id=request.args.get('id')
    data=subscriber.query.filter_by(identifier=id).update({"status":"运行中"})
    db.session.commit()
    return jsonify({"result":"success"})


@quant_api.route('/realtime_simulation',methods=('GET', 'POST'))
def get_realtime_simulation_data():
    data = subscriber.query.filter_by(user=current_user.username).join(strategy).add_columns(strategy.name_cn).all()
    result=[]
    if not data:
        return jsonify({"flag":"empty"})
    for each in data:
        result.append([each[0].identifier,each[0].strategy_name,each.name_cn,sql_to_dict(each[0].parameter)['cash'],'N/A',each[0].status,each[0].build_date.strftime("%Y年%m月%d日"),''])
    return jsonify({"flag":"exist","data":result})

@quant_api.route('/realtime_simulation_detail',methods=('GET', 'POST'))
def get_realtime_simulation_detail_data():
    id=request.args.get('id')
    data=subscriber.query.filter_by(identifier=id).first()
    if data:
        params=sql_to_dict(data.parameter)
        if data.strategy_id == Strategy.Pair_Strategy_Based_Bank.value:
            strategy = Strategy_Manager(Strategy.Pair_Strategy_Based_Bank, live=True, cash=params['cash'],
                                        commission=params['commission'], builddate=data.build_date,
                                        instrument_1=params['instrument_1'], instrument_2=params['instrument_2'])
            strategy.run()
            message = strategy.getMessage()

        if data.strategy_id == Strategy.DoubleMA_Strategy.value:
            strategy = Strategy_Manager(Strategy.DoubleMA_Strategy, live=True, cash=params['cash'],
                                        commission=params['commission'], builddate=data.build_date,
                                        instrument=params['instrument'])
            strategy.run()
            message = strategy.getMessage()
        if data.strategy_id == Strategy.Buy_Everyday.value:
            strategy = Strategy_Manager(Strategy.Buy_Everyday, live=True, cash=params['cash'],
                                        commission=params['commission'], builddate=data.build_date,
                                        instrument=params['instrument'])
            strategy.run()
            message = strategy.getMessage()
        keys=message.keys()
        keys.sort()
        date_list =[key.strftime("%Y-%m-%d")  for key in keys]
        message_list=map(message.get,keys)
        return jsonify({"date":date_list,"message":message_list})
    else:
        return jsonify({"date":[],"message":[]})

@quant_api.route('/subscribe_strategy_info',methods=('GET', 'POST'))
def get_subscribe_strategy_info():
    id=request.args.get('id')
    data=subscriber.query.filter_by(identifier=id).join(strategy).add_columns(strategy.name_cn,strategy.type,strategy.name_en).first()
    delta=datetime.datetime.now()-data[0].build_date
    result={"strategy_name":data[0].strategy_name,"params":sql_to_dict(data[0].parameter),"status":data[0].status,"build_date":data[0].build_date.strftime("%Y-%m-%d"),"str_name":data.name_cn,"type":data.type,"str_name_en":data.name_en,"period":delta.days}
    return jsonify(result)

@quant_api.route('/get_models',methods=('GET', 'POST'))
def get_models():
    result=[]
    data=strategy.query.filter().all()
    for each in data:
        result.append({"name_en":each.name_en,"name_cn":each.name_cn,"type":each.type,"description":each.description,"id":each.id})
    return jsonify(result)
