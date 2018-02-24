# encoding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify, flash
from webapp.models import *
import MySQLdb, time, re
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker
from flask_login import current_user
import math
import string
from collections import Counter
import tushare as ts
import gc
import pandas as pd
from datetime import datetime
from datetime import timedelta
from  webapp.stratlib import *

message_api = Blueprint(
    'message_api',
    __name__,
    url_prefix="/message_api"
)


@message_api.route('/request_page', methods=['GET', 'POST'])
def request_page():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    result = session.query(func.count(input_message.post_id).label("page_num")).first()

    data['page_num'] = math.ceil((result.page_num) / float(5))

    return jsonify(data)


@message_api.route('/person_box', methods=['GET', 'POST'])
def person_box():
    data = {}

    postid = int(request.args.get('postID'))
    querypost = input_message.query.filter_by(post_id=postid).first()
    personid = querypost.poster

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    fb = session.query(func.count(input_message.post_id).label("postnum")).filter(
        input_message.poster == personid).first()

    gz = session.query(func.count(follows.followed).label("followednum")).filter(
        follows.follower == personid).first()

    fs = session.query(func.count(follows.follower).label("followernum")).filter(
        follows.followed == personid).first()

    data['postnum'] = fb.postnum
    data['followednum'] = gz.followednum
    data['followernum'] = fs.followernum

    return jsonify(data)


@message_api.route('/to_input_text', methods=['GET', 'POST'])
def to_input_text():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputtext = request.form.get('input_text')

    result = session.query(func.count(input_message.post_id).label("post_id")).first()

    my_input = input_message()
    my_input.post_id = result.post_id
    my_input.poster = current_user.username
    my_input.post_text = inputtext
    my_input.comment_num = 0
    my_input.retrant_num = 0
    my_input.upvote_num = 0
    my_input.if_retrant = 0
    my_input.post_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.session.add(my_input)
    db.session.commit()
    data['value'] = 'success'

    return jsonify(data)


@message_api.route('/message_all', methods=['GET', 'POST'])
def message_all():
    data = {}

    id = []
    user = []
    text = []
    time = []
    comment = []
    retrant = []
    upvote = []
    ifretrant = []
    retrantposter = []
    retranttext = []

    page = int(request.args.get('page_num'))
    minpage = 5 * page
    maxpage = 5 * (page + 1)

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    number = session.query(func.count(input_message.post_id).label("page_num")).first()
    x = number.page_num
    min = x - maxpage
    max = x - minpage

    results = input_message.query.filter(input_message.post_id >= min, input_message.post_id < max).all()

    for result in results:
        id.append(result.post_id)
        user.append(result.poster)
        text.append(result.post_text)
        time.append(result.post_time)
        comment.append(result.comment_num)
        retrant.append(result.retrant_num)
        upvote.append(result.upvote_num)
        ifretrant.append(result.if_retrant)
        retrantposter.append(result.retrant_poster)
        retranttext.append(result.retrant_text)

    data['po_id'] = id
    data['po_user'] = user
    data['po_text'] = text
    data['po_time'] = time
    data['po_comment'] = comment
    data['po_retrant'] = retrant
    data['po_upvote'] = upvote
    data['po_ifretrant'] = ifretrant
    data['po_retrant_poster'] = retrantposter
    data['po_retrant_text'] = retranttext

    return jsonify(data)


@message_api.route('/comment_all', methods=['GET', 'POST'])
def comment_all():
    data = {}

    mypost = int(request.args.get('post'))

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    mypage = session.query(func.count(comments.post_id).label("page_num")).filter(comments.post_id == mypost).first()

    page = math.ceil(mypage.page_num / float(5))

    id = []
    commenter = []
    text = []
    time = []

    results = comments.query.filter(comments.post_id == mypost).all()

    for result in results:
        id.append(result.comment_id)
        commenter.append(result.commenter)
        text.append(result.comment_text)
        time.append(result.comment_time)

    data['co_id'] = id
    data['co_post'] = mypost
    data['co_commenter'] = commenter
    data['co_text'] = text
    data['co_time'] = time
    data['co_page'] = page

    return jsonify(data)


@message_api.route('/to_comment', methods=['GET', 'POST'])
def to_comment():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputcomment = request.form.get('input_comment')
    inputpost = request.form.get('input_post')

    result = session.query(func.count(comments.comment_id).label("comment_id")).first()

    my_input_comment = comments()
    my_input_comment.comment_id = result.comment_id
    my_input_comment.post_id = inputpost
    my_input_comment.commenter = current_user.username
    my_input_comment.comment_text = inputcomment
    my_input_comment.comment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.session.add(my_input_comment)
    db.session.commit()

    postresult = input_message.query.filter_by(post_id=inputpost).first()
    newdata = postresult.comment_num + 1
    input_message.query.filter_by(post_id=inputpost).update({'comment_num': newdata})
    db.session.commit()

    data['value'] = 'success'

    return jsonify(data)


@message_api.route('/to_upvote', methods=['GET', 'POST'])
def to_upvote():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputpost = request.form.get('input_post')

    postresult = input_message.query.filter_by(post_id=inputpost).first()
    newdata = postresult.upvote_num + 1
    input_message.query.filter_by(post_id=inputpost).update({'upvote_num': newdata})
    db.session.commit()

    data['value'] = 'success'

    return jsonify(data)


@message_api.route('/query_follow', methods=['GET', 'POST'])
def query_follow():
    data = 0

    thisposter = request.args.get('myposter')
    thisuser = current_user.username

    result = follows.query.filter_by(follower=thisuser, followed=thisposter).first()

    if result:
        data = 1
    else:
        data = 0

    return jsonify(data)


@message_api.route('/to_follow', methods=['GET', 'POST'])
def to_follow():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputpost = request.form.get('input_post')

    result = input_message.query.filter_by(post_id=inputpost).first()

    my_input_follow = follows()
    my_input_follow.followed = result.poster
    my_input_follow.follower = current_user.username

    db.session.add(my_input_follow)
    db.session.commit()

    data['value'] = 'success'

    return jsonify(data)


@message_api.route('/no_follow', methods=['GET', 'POST'])
def no_follow():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputpost = request.form.get('input_post')

    result = input_message.query.filter_by(post_id=inputpost).first()

    follows.query.filter_by(followed=result.poster, follower=current_user.username).delete()
    db.session.commit()

    data['value'] = 'success'

    return jsonify(data)


@message_api.route('/to_retrant', methods=['GET', 'POST'])
def to_retrant():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    getid = request.form.get('get_id')
    gettext = request.form.get('get_text')

    myresult = input_message.query.filter_by(post_id=getid).first()

    if myresult.if_retrant == 0:
        inputposter = myresult.poster
        inputtext = myresult.post_text
    else:
        inputposter = myresult.retrant_poster
        inputtext = myresult.retrant_text

    newdata = myresult.retrant_num + 1
    input_message.query.filter_by(post_id=getid).update({'retrant_num': newdata})
    db.session.commit()

    result = session.query(func.count(input_message.post_id).label("post_id")).first()

    my_input = input_message()
    my_input.post_id = result.post_id
    my_input.poster = current_user.username
    my_input.post_text = gettext
    my_input.comment_num = 0
    my_input.retrant_num = 0
    my_input.upvote_num = 0
    my_input.if_retrant = 1
    my_input.retrant_poster = inputposter
    my_input.retrant_text = inputtext
    my_input.post_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db.session.add(my_input)
    db.session.commit()

    data['value'] = 'success'

    return jsonify(data)
