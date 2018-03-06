from flask import Blueprint, redirect, render_template, url_for, request
from webapp.config import paths
import os
from flask_login import login_required, current_user

message_view = Blueprint(
    'message',
    __name__,
    template_folder=os.path.abspath(os.path.join(paths.project_path,'webapp','Template', 'message')),
    url_prefix="/message"
)

@message_view.route('/my_message', methods=('GET', 'POST'))
@login_required
def my_message():
    return render_template('my_message.html')

@message_view.route('/system_message',methods=('GET', 'POST'))
@login_required
def system_message():
    return render_template('system_message.html')