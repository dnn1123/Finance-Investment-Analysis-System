# encoding:utf-8
from flask import Blueprint, redirect, render_template, url_for
from os import path
from flask_login import login_required, current_user

stock_blueprint = Blueprint(
    'stock',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'stock'),
    url_prefix="/stock"
)


# 用户登陆后主页
@stock_blueprint.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("stock/home.html")

@stock_blueprint.route('/myposition/', methods=['GET', 'POST'])
@login_required
def myposition():
    return render_template('myposition.html', current_user=current_user)