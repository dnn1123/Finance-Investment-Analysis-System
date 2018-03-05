# coding=utf-8
from flask import Blueprint,request,render_template,jsonify
from flask_login import current_user
from .bpm import handle_form,handle_liveform,dict_to_sql,sql_to_dict,Strategy_Manager,Strategy
from webapp.stratlib import Profit_monitoring
from webapp.models import strategy,subscriber,db
import os,datetime
from time import sleep
quant_api = Blueprint(
    'quant_api',
    __name__,
    template_folder=os.path.abspath(os.path.join(os.getcwd(),'webapp','Template','quant')),
    url_prefix="/quant_api"
)

@quant_api.route('/backtest_form', methods=('GET', 'POST'))
def request_form():
    type=request.args.get('type')
    if type=="Pair_Strategy_Based_Bank":
        return render_template('/form/form_Pair_Strategy_Based_Bank.html')
    if type=="DoubleMA_Strategy":
        return render_template('/form/form_DoubleMA_Strategy.html')
@quant_api.route('/backtest', methods=('GET', 'POST'))
def back_test():
    data,history=handle_form(request.form)
    getdata = Profit_monitoring(history)
    results = getdata.start()
    print(results)
    return jsonify(data)

@quant_api.route('/realtime_form', methods=('GET', 'POST'))
def request_liveform():
    type=request.args.get('type')
    if type=="Pair_Strategy_Based_Bank":
        return render_template('/form/liveform_Pair_Strategy_Based_Bank.html')
    if type=="DoubleMA_Strategy":
        return render_template('/form/liveform_DoubleMA_Strategy.html')
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
