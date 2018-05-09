from flask import Blueprint, redirect, render_template, url_for, request
from webapp.config import paths
import os
from flask_login import login_required, current_user
import time as Time

message_view = Blueprint(
    'message',
    __name__,
    template_folder=os.path.abspath(os.path.join(paths.project_path, 'Template', 'message')),
    url_prefix="/message"
)


@message_view.route('/my_message', methods=('GET', 'POST'))
@login_required
def my_message():
    i = 0
    a = Time.strftime('%Y%m%d%H%M%S', Time.localtime(Time.time()))
    b = bytes(current_user.username)
    x = b + bytes(a)
    if request.method == 'POST':
        myfile = request.files.getlist('file')
        for f in myfile:
            i = i + 1
            newname = x + bytes(i) + '.jpg'
            upload_path = os.path.abspath(os.path.join(paths.project_path, 'static', 'a_photo', newname))
            f.save(upload_path)
        return render_template('my_message.html', current_user=current_user, name=x, number=i)
    else:
        return render_template('my_message.html', current_user=current_user, name=x, number=i)


@message_view.route('/system_message', methods=('GET', 'POST'))
@login_required
def system_message():
    return render_template('system_message.html')
