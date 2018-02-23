# coding=utf-8
from flask import Flask, redirect, url_for, render_template
from flask_principal import identity_loaded, UserNeed, RoleNeed
from config import DevConfig
from controllers.stock import stock_blueprint
from controllers.main import main_blueprint
from controllers.stock_solo import stocksolo_blueprint
from controllers.stock_group import stockgroup_blueprint  # me
from controllers.global_industry import globalindustry_blueprint  # me
from controllers.industry_analysis import industryanalysis_blueprint  # me
from controllers.invest_env import investenv_blueprint  # me
from forms import CodeForm
from datetime import datetime
from extensions import login_manager, principals
from models import db
from flask_login import current_user
from controllers.restfulapi import api_blueprint
# from webapp.admin import create_admin
from Controller.main.view import main_view
from Controller.main.api import main_api
from Controller.stock_group.view import stock_group_view
from Controller.stock_group.api import stock_group_api
from Controller.quant.view import quant_view
from Controller.quant.api import quant_api

def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(DevConfig)
    # create_admin(app)
    login_manager.init_app(app)
    principals.init_app(app)
    db.init_app(app)
    #模块注册
    app.register_blueprint(stock_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(stocksolo_blueprint)
    app.register_blueprint(stockgroup_blueprint)
    app.register_blueprint(globalindustry_blueprint)
    app.register_blueprint(industryanalysis_blueprint)
    app.register_blueprint(investenv_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(main_view)
    app.register_blueprint(main_api)
    app.register_blueprint(stock_group_view)
    app.register_blueprint(stock_group_api)
    app.register_blueprint(quant_view)
    app.register_blueprint(quant_api)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        identity.user = current_user
        if hasattr(current_user, "username"):
            identity.provides.add(UserNeed(current_user.username))
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    return app
