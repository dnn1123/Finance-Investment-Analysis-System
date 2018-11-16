# -*- coding: utf-8 -*-：
from flask_admin import Admin
from views import *
from webapp.models import *
from flask.ext.admin import AdminIndexView, expose

# def create_admin(app=None):
#     # admin = Admin(app)
#     admin = Admin(app,name="FIAS", index_view=MyIndexView(), base_template='admin/my_master.html')
#     if(UserView.is_accessible):
#         admin.add_view(UserView(db.session, name=u'用户列表'))
#     if(User_Role_View.is_accessible):
#         admin.add_view(User_Role_View(db.session, name=u'用户权限'))