# coding=utf-8
import os
from flask import Blueprint, redirect, url_for, flash, render_template, current_app, request, jsonify
from webapp.forms import LoginForm, RegisterForm
from webapp.models import users, db, Permission
from flask_login import login_user, login_required, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from webapp.decorators import admin_required, permission_required
from webapp.models import *
from webapp.sms import *
import random

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)

Verification_code_list = {}


# 登录界面
@main_blueprint.route('/')
def index():
    return redirect(url_for('main.login'))


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    register_form = RegisterForm()
    if form.validate_on_submit():
        user = users.query.filter_by(username=form.username.data).one()
        login_user(user, remember=form.remember.data)
        identity_changed.send(
            current_app._get_current_object(),
            identity=Identity(user.username)
        )
        # phone = "13234045805"
        # text = "【253云通讯】您的验证码是1234"
        # send_sms(text, phone)
        flash("You have been logged in", category="success")
        return redirect(url_for('stock.home', usersname=user.username))
    return render_template('main/login.html', form=form, register_form=register_form)


@main_blueprint.route('/profilephoto/', methods=['GET', 'POST'])
def profilephoto():
    if request.method == 'POST':
        f = request.files['file']
        newname = current_user.username + '.jpg'
        upload_path = os.path.join(os.getcwd(), 'webapp', 'static', 'avatar', newname)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
    return render_template('main/profilephoto.html', current_user=current_user)


@main_blueprint.route('/personal/', methods=['GET', 'POST'])
def personal():
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    role = Role.query.filter_by(id=user.permissions).first()
    rolename = role.description
    return render_template('personal/person.html', user=user, rolename=rolename)


@main_blueprint.route('/myposition/', methods=['GET', 'POST'])
@login_required
def analysis():
    return render_template('personal/analysis.html', current_user=current_user)


# 手机注册
@main_blueprint.route('/register_phone', methods=['GET', 'POST'])
def register_phone():
    phone_number = request.args.get('phone_number')
    password = request.args.get('password')
    confirm_password = request.args.get('confirm_password')
    Verification_code = request.args.get('Verification_code')
    data = {}

    if Verification_code_list[phone_number] == Verification_code:
        new_user = users()
        new_user.username = phone_number
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        new_user_role = users_roles()
        new_user_role.user_name = phone_number
        new_user_role.permissions = 3
        db.session.add(new_user_role)
        db.session.commit()
        data['msg'] = 'success'
        return jsonify(data)
    data['msg'] = 'failure'
    return jsonify(data)


# 发送验证码短信
@main_blueprint.route('/send_Verification_code', methods=['GET', 'POST'])
def send_Verification_code():
    phone_number = request.args.get('phone_number')
    data = {}
    # 判断是否已经注册
    result = users.query.filter_by(username=phone_number).first()
    if result:
        data['exit'] = 'true'
        data['aaa'] = result.username
        return jsonify(data)
    else:
        data['exit'] = 'flase'
        Verification_code = str(random.randint(100000, 999999))
        Verification_code_list[phone_number] = Verification_code
        text = '【中勋科技】您的验证码是' + Verification_code
        send_sms(text, phone_number)
        data['phone_number'] = phone_number
        data['Verification_code'] = Verification_code

        return jsonify(data)


@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = users()
        new_user.username = register_form.username.data
        new_user.set_password(register_form.password.data)
        db.session.add(new_user)
        db.session.commit()

        new_user_role = users_roles()
        new_user_role.user_name = register_form.username.data
        new_user_role.permissions = 3
        db.session.add(new_user_role)
        db.session.commit()

        flash(
            "注册成功！请登录",
            category="success"
        )
        return redirect(url_for('.login'))
    else:
        return redirect(url_for('.login'))


@main_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity()
    )
    return redirect(url_for('main.login'))


@main_blueprint.route('/test')
def test():
    return render_template('test.html')


@main_blueprint.route('/my_favoritecode/', methods=['GET', 'POST'])
def my_favoritecode():
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    role = Role.query.filter_by(id=user.permissions).first()
    rolename = role.description
    return render_template('personal/my_favoritecode.html', user=user, rolename=rolename)


@main_blueprint.route('/admin/', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.administrator)
def admin():
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    role = Role.query.filter_by(id=user.permissions).first()
    rolename = role.description
    return render_template('admin/admin_permission.html', user=user, rolename=rolename)
