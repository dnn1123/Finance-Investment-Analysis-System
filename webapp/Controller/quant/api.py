# coding=utf-8
from flask import Blueprint,request,render_template,jsonify
from bpm import handle_form
from webapp.stratlib import Profit_monitoring
import os
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
