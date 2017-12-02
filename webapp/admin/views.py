# -*- coding: utf-8 -*-：
from flask.ext.admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from webapp.models import *
from flask_login import login_required,current_user
from webapp.decorators import admin_required,permission_required


class MyIndexView(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        return super(MyIndexView, self).index()


class UserView(ModelView):

    can_create = False
    column_labels = {
        'username':u'用户名',
        'password': u'密码',
    }
    column_list = ('username', 'password')

    def __init__(self, session, **kwargs):
        super(UserView, self).__init__(users, session, **kwargs)

class User_Role_View(ModelView):
    can_create = False
    column_labels = {
        'id':u'序号',
        'user_name':u'用户名',
        'permissions': u'权限等级',
    }
    column_list = ('id', 'user_name','permissions')

    def __init__(self, session, **kwargs):
        super(User_Role_View, self).__init__(roles1, session, **kwargs)