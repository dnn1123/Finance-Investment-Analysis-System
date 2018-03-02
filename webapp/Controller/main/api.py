#encoding:utf-8
from flask import Blueprint,request,redirect,render_template,current_app,url_for,jsonify
from flask_login import login_user
from flask_principal import identity_changed,Identity
from webapp.models import users,users_roles,db
from webapp.sms import send_sms
from webapp.config import paths
import os,random
main_api = Blueprint(
    'main_api',
    __name__,
    template_folder=os.path.abspath(os.path.join(paths.project_path, 'webapp', 'Template', 'main')),
    url_prefix="/main_api"
)
Verification_code_list = {}
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

@main_api.route('/register_info',methods=['GET', 'POST'])
def register():
    username=request.form.get('user')
    password=request.form.get('pwd')
    cpassword=request.form.get('cpwd')
    user = users.query.filter_by(username=username).first()
    if user:
        return render_template('register.html',error=u'用户名已存在')
    if password!=cpassword:
        return render_template('register.html',error=u'密码不一致')
    new_user = users()
    new_user.username = username
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    new_user_role = users_roles()
    new_user_role.user_name = username
    new_user_role.permissions = 3
    db.session.add(new_user_role)
    db.session.commit()
    return redirect(url_for('main.index'))


# 手机注册
@main_api.route('/register_phone_info', methods=['GET', 'POST'])
def register_phone():
    phone_number = request.args.get('phone_number')
    password = request.args.get('password')
    confirm_password = request.args.get('confirm_password')
    Verification_code = request.args.get('Verification_code')
    data = {}
    if Verification_code_list[phone_number] == Verification_code:
        if password==confirm_password:
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
@main_api.route('/send_Verification_code', methods=['GET', 'POST'])
def send_Verification_code():
    phone_number = request.args.get('phone_number')
    data = {}
    # 判断是否已经注册
    result = users.query.filter_by(username=phone_number).first()
    if result:
        data['exit'] = 'true'
        data['aaa'] =  result.username
        return jsonify(data)
    else:
        data['exit'] = 'flase'
        Verification_code = str(random.randint(100000,999999))
        Verification_code_list[phone_number] = Verification_code
        text = '【魔法金融】您的验证码是' + Verification_code
        send_sms(text, phone_number)
        data['phone_number'] = phone_number
        data['Verification_code'] = Verification_code

        return jsonify(data)