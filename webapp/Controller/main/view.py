#encoding:utf-8
from flask import Blueprint,render_template
import os
main_view = Blueprint(
    'main_new',
    __name__,
    template_folder=os.path.abspath(os.path.join(os.getcwd(),'webapp','Template','main')),
    url_prefix="/"
)

@main_view.route('/',methods=['GET', 'POST'])
def index():
    return render_template('login.html')

@main_view.route('/register',methods=['GET', 'POST'])
def register():
    return render_template('regieter.html')