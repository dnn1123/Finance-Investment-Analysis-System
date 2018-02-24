# coding=utf-8
from flask import Blueprint,render_template
import os

quant_view = Blueprint(
    'quant',
    __name__,
    template_folder=os.path.abspath(os.path.join(os.getcwd(),'webapp','Template','quant')),
    url_prefix="/quant"
)

@quant_view.route('/backtest', methods=('GET', 'POST'))
def backtest():
    return render_template('backtest.html')

@quant_view.route('/realtime_simulation', methods=('GET', 'POST'))
def realtime_simulation():
    return  render_template('realtime_simulation.html')


@quant_view.route('/realtime_simulation/test', methods=('GET', 'POST'))
def realtime_simulation_detail():
    return  render_template('realtime_simulation_detail.html')