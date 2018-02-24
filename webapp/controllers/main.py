# coding=utf-8
from flask import Blueprint, redirect, url_for, flash, render_template, current_app,request, jsonify
from webapp.forms import LoginForm, RegisterForm
from webapp.models import users, db,Permission
from flask_login import login_user, login_required, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed

from webapp.models import *
from webapp.sms import *
import random





# # 登录界面
# @main_blueprint.route('/oldpage')
# def index():
#     return redirect(url_for('main.login'))


# @main_blueprint.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     register_form = RegisterForm()
#     if form.validate_on_submit():
#         user = users.query.filter_by(username=form.username.data).one()
#         login_user(user, remember=form.remember.data)
#         identity_changed.send(
#             current_app._get_current_object(),
#             identity=Identity(user.username)
#         )
#         # phone = "13234045805"
#         # text = "【253云通讯】您的验证码是1234"
#         # send_sms(text, phone)
#         flash("You have been logged in", category="success")
#         return redirect(url_for('stock.home',usersname=user.username))
#     return render_template('main/login.html', form=form, register_form=register_form)









# @main_blueprint.route('/register', methods=['GET', 'POST'])
# def register():
#     register_form = RegisterForm()
#     if register_form.validate_on_submit():
#         new_user = users()
#         new_user.username = register_form.username.data
#         new_user.set_password(register_form.password.data)
#         db.session.add(new_user)
#         db.session.commit()
#
#         new_user_role = users_roles()
#         new_user_role.user_name = register_form.username.data
#         new_user_role.permissions = 3
#         db.session.add(new_user_role)
#         db.session.commit()
#
#         flash(
#             "注册成功！请登录",
#             category="success"
#         )
#         return redirect(url_for('.login'))
#     else:
#         return redirect(url_for('.login'))



