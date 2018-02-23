# coding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request  # me:request
import os
from webapp.models import *
from webapp.forms import *
from flask_login import login_required, current_user
from webapp.extensions import finance_analyst_permission
# from flask_sqlalchemy import SQLAlchemy #me
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me
import MySQLdb, time

stock_group_view = Blueprint(
    'stock_group',
    __name__,
    template_folder=os.path.abspath(os.path.join(os.getcwd(),'webapp','Template','stock_group')),
    url_prefix="/stock_group"
)

# 市场导航
@stock_group_view.route('/navigation', methods=('GET', 'POST'))
@login_required
def navigation():
    return render_template('navigation.html')

# cns 大陆市场
@stock_group_view.route('/cns_home', methods=('GET', 'POST'))
@login_required
def cns_home():
    return render_template("cns/cns_stock_industry.html")

# 沪深300指数筛选
@stock_group_view.route('/hushen_300', methods=('GET', 'POST'))
@login_required
def hushen_300():
    return render_template("/cns/cns_hushen_300.html")


# 上证50指数筛选
@stock_group_view.route('/shangzheng_50', methods=('GET', 'POST'))
@stock_group_view.route('/shangzheng_50/<string:trade_code>', methods=('GET', 'POST'))
@login_required
def shangzheng_50():
    return render_template("cns/cns_shangzheng_50.html")


# 陆股通指数筛选
@stock_group_view.route('/lugutong', methods=('GET', 'POST'))
@login_required
def lugutong():
    return render_template("cns/cns_lugutong.html")


# cnsb 沪深交易所B股公司
@stock_group_view.route('/cnsb_home', methods=('GET', 'POST'))
@stock_group_view.route('/cnsb_home/<string:trade_code>', methods=('GET', 'POST'))
@login_required
def cnsb_home():
    return render_template("cns/cnsb_stock_industry.html")