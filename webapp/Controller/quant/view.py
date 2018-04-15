# coding=utf-8
from flask import Blueprint,render_template
from webapp.config import paths
import os

quant_view = Blueprint(
    'quant',
    __name__,
    template_folder=os.path.abspath(os.path.join(paths.project_path,'Template','quant')),
    url_prefix="/quant"
)
@quant_view.route('/models',methods=('GET', 'POST'))
def models():
    return render_template('models.html')

@quant_view.route('/models_sample/',methods=('GET', 'POST'))
@quant_view.route('/models_sample/<string:pic>',methods=('GET', 'POST'))
def models_sample(pic="None"):
    return render_template('models_sample.html',pic=pic)

@quant_view.route('/backtest', methods=('GET', 'POST'))
def backtest():
    return render_template('backtest.html')

@quant_view.route('/realtime_simulation/', methods=('GET', 'POST'))
def realtime_simulation():
    return  render_template('realtime_simulation.html')

@quant_view.route('/realtime_simulation/<string:id>', methods=('GET', 'POST'))
def realtime_simulation_detail(id):
    return  render_template('realtime_simulation_detail.html',subscribe_id=id)
