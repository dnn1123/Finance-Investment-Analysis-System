#encoding:utf-8
from flask import Blueprint,request,redirect,render_template,current_app,url_for
from flask_login import login_user
from flask_principal import identity_changed,Identity
from webapp.models import users
import os
main_api = Blueprint(
    'main_api',
    __name__,
    template_folder=os.path.abspath(os.path.join(os.getcwd(), 'webapp', 'Template', 'main')),
    url_prefix="/main_api"
)

@main_api.route('/login_info',methods=['GET', 'POST'])
def login():
    username=request.form.get('user')
    password=request.form.get('pwd')
    if request.form.get('rmb') is None:
        remember=False
    else:
        remember=True
    user=users.query.filter_by(username=username).first()
    if not user:
        return render_template('login.html',error=u"用户不存在")
    if not user.check_password(password):
        return render_template('login.html',error=u"密码不匹配")
    login_user(user, remember=remember)
    identity_changed.send(
         current_app._get_current_object(),
         identity=Identity(user.username)
    )
    return redirect(url_for('stock.home',usersname=user.username))