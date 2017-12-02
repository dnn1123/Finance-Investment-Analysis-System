# encoding:utf-8
from flask import Blueprint, redirect, render_template, url_for
from os import path
from webapp.extensions import finance_analyst_permission
from flask_principal import Permission, UserNeed, RoleNeed
from flask_login import login_required, current_user
from  webapp.models import *

stock_blueprint = Blueprint(
    'stock',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'stock'),
    url_prefix="/stock"
)


# 用户登陆后主页
@stock_blueprint.route('/home', methods=('GET', 'POST'))
@login_required
def home():
    # roles = current_user.roles
    # user = roles1.query.filter_by(user_name=current_user.username).first()
    # # id = roles1.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    return render_template("stock/home.html")
