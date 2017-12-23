# -*- coding: utf-8 -*-：
from flask.ext.admin import AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from webapp.models import *
from flask_login import login_required, current_user
from webapp.decorators import admin_required,permission_required


class MyIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return super(MyIndexView, self).index()


class UserView(ModelView):

    def is_accessible(self):
        if current_user.can(Permission.administrator):
            return True
        return False
    can_create = False

    column_labels = {
        'username':u'用户名',
        # 'password': u'密码',
    }
    column_list = ('username',)

    def __init__(self, session, **kwargs):
        super(UserView, self).__init__(users, session, **kwargs)


class User_Role_View(ModelView):

    def is_accessible(self):
        if current_user.can(Permission.administrator):
            return True
        return False
    can_create = False

    column_labels = {
        'id':u'序号',
        'user_name':u'用户名',
        'permissions': u'权限等级',
        'permissions_name': u'权限描述',
    }
    column_list = ('id', 'user_name','permissions','permissions_name')
    def __init__(self, session, **kwargs):
        super(User_Role_View, self).__init__(users_roles, session, **kwargs)