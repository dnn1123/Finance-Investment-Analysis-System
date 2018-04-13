#encoding:utf-8
from flask import Blueprint,render_template,current_app,redirect,url_for,request
from flask_login import login_required,logout_user,current_user
from flask_principal import identity_changed,AnonymousIdentity
from webapp.decorators import permission_required
from webapp.models import users_roles,Role,Permission
from webapp.config import paths
import os

main_view = Blueprint(
    'main',
    __name__,
    template_folder=os.path.abspath(os.path.join(paths.project_path, 'Template', 'main')),
    url_prefix="/"
)


@main_view.route('/', methods=['GET', 'POST'])
def index():
    return render_template('new_login.html')


@main_view.route('register_phone', methods=['GET', 'POST'])
def register_phone():
    return render_template('register_phone.html')


@main_view.route('register', methods=['GET', 'POST'])
def register():
    return render_template('new_register.html')


@main_view.route('logout')
@login_required
def logout():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity()
    )
    return redirect(url_for('main.index'))


@main_view.route('profilephoto', methods=['GET', 'POST'])
def profilephoto():

    if request.method == 'POST':
        f = request.files['file']
        newname = current_user.username + '.jpg'
        upload_path = os.path.join(os.getcwd(), 'webapp', 'static', 'avatar', newname)  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        return render_template('profilephoto.html', current_user=current_user)
    else:
        return render_template('profilephoto.html', current_user=current_user)


@main_view.route('personal', methods=['GET', 'POST'])
def personal():
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    role = Role.query.filter_by(id=user.permissions).first()
    rolename = role.description
    return render_template('personal/person.html', user=user, rolename=rolename)


@main_view.route('myposition', methods=['GET', 'POST'])
@login_required
def analysis():
    return render_template('personal/analysis.html', current_user=current_user)


@main_view.route('my_favoritecode', methods=['GET', 'POST'])
def my_favoritecode():
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    role = Role.query.filter_by(id=user.permissions).first()
    rolename = role.description
    return render_template('personal/my_favoritecode.html', user=user, rolename=rolename)


@main_view.route('admin', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.administrator)
def admin():
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    # rolename = Role.query.filter_by(id=user.permissions).first()
    role = Role.query.filter_by(id=user.permissions).first()
    rolename = role.description
    return render_template('admin/admin_permission.html', user=user, rolename=rolename)
