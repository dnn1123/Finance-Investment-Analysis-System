# coding=utf-8
from flask import Blueprint, redirect, url_for, flash, render_template, current_app
from webapp.forms import LoginForm, RegisterForm
from webapp.models import users, db,Permission
from flask_login import login_user, login_required, logout_user, current_user
from flask_principal import Identity, AnonymousIdentity, identity_changed
from webapp.decorators import admin_required,permission_required
from webapp.models import *
main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)


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
        flash("You have been logged in", category="success")
        return redirect(url_for('stock.home',usersname=user.username))
    return render_template('main/login.html', form=form, register_form=register_form)


@main_blueprint.route('/personal/', methods=['GET', 'POST'])
def personal():
    user = roles1.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    role = Role.query.filter_by(id=user.permissions).first()
    rolename = role.description
    return render_template('personal/person.html',user=user,rolename=rolename)





@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = users()
        new_user.username = register_form.username.data
        new_user.set_password(register_form.password.data)
        db.session.add(new_user)
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


