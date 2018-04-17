# coding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify, flash
from webapp.models import *
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker
from flask_login import current_user
import math
import string
import os
import time as Time
from  webapp.stratlib import *

message_api = Blueprint(
    'message_api',
    __name__,
    url_prefix="/message_api"
)


# 用于获取分页总数
@message_api.route('/request_page', methods=['GET', 'POST'])
def request_page():
    data = {}
    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    result = session.query(func.count(input_message.post_id).label("page_num")).first()
    data['page_num'] = math.ceil((result.page_num) / float(5))
    # 查询用户未读消息
    sender_list = []
    info_list = []
    text_list = []
    id_list = []
    time_list = []
    state_list = []
    username = current_user.username
    results = personal_information.query.filter_by(receiver=username).all()
    for result in results:
        if result.sender !='system':
            sender_list.append(result.sender)
            info_list.append(result.message_content)
            text_list.append(result.message_text)
            id_list.append(result.id)
            time_list.append(result.time)
            state_list.append(result.state)
    data['sender_list'] = sender_list
    data['info_list'] = info_list
    data['text_list'] = text_list
    data['id_list'] = id_list
    data['time_list'] = time_list
    data['state_list'] = state_list

    return jsonify(data)


@message_api.route('/request_follow_page', methods=['GET', 'POST'])
def request_follow_page():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    result = session.query(func.count(input_message.post_id).label("page_num")).filter(
        input_message.poster == follows.followed).filter(follows.follower == current_user.username).first()

    data['page_num'] = math.ceil((result.page_num) / float(5))

    return jsonify(data)


@message_api.route('/request_myown_page', methods=['GET', 'POST'])
def request_myown_page():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    result = session.query(func.count(input_message.post_id).label("page_num")).filter(
        input_message.poster == current_user.username).first()

    data['page_num'] = math.ceil((result.page_num) / float(5))

    return jsonify(data)


# 用于展示个人信息悬浮框
@message_api.route('/person_box', methods=['GET', 'POST'])
def person_box():
    data = {}

    postid = int(request.args.get('postID'))
    queryposter = input_message.query.filter(input_message.post_id == postid).first()
    personid = queryposter.poster

    queryavatar = personal.query.filter(personal.username == personid).first()

    if queryavatar:
        if queryavatar.avatar is not None:
            myavatar = queryavatar.avatar
        else:
            myavatar = 'user.png'
    else:
        myavatar = 'user.png'

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    fb = session.query(func.count(input_message.post_id).label("postnum")).filter(
        input_message.poster == personid).first()

    gz = session.query(func.count(follows.followed).label("followednum")).filter(
        follows.follower == personid).first()

    fs = session.query(func.count(follows.follower).label("followernum")).filter(
        follows.followed == personid).first()

    data['my_avatar'] = myavatar
    data['postnum'] = fb.postnum
    data['followednum'] = gz.followednum
    data['followernum'] = fs.followernum

    return jsonify(data)


# 用于发布动态
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


# 用于展示用户动态
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
    avatar = []

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

    profilephoto = personal.query.filter(personal.username == current_user.username).first()
    if profilephoto:
        if profilephoto.avatar is not None:
            current_avatar = profilephoto.avatar
        else:
            current_avatar = 'user.png'
    else:
        current_avatar = 'user.png'

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

        name = result.poster
        myresult = personal.query.filter(personal.username == name).first()
        if myresult:
            if myresult.avatar is not None:
                avatar.append(myresult.avatar)
            else:
                avatar.append('user.png')
        else:
            avatar.append('user.png')

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
    data['avatar'] = avatar
    data['current_user'] = current_avatar

    return jsonify(data)


@message_api.route('/message_follow', methods=['GET', 'POST'])
def message_follow():
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
    avatar = []

    page = int(request.args.get('page_num'))
    minpage = 5 * page
    maxpage = 5 * (page + 1)

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    number = session.query(func.count(input_message.post_id).label("page_num")).filter(
        input_message.poster == follows.followed).filter(follows.follower == current_user.username).first()

    profilephoto = personal.query.filter(personal.username == current_user.username).first()
    if profilephoto:
        if profilephoto.avatar is not None:
            current_avatar = profilephoto.avatar
        else:
            current_avatar = 'user.png'
    else:
        current_avatar = 'user.png'

    results = input_message.query.filter(
        input_message.poster == follows.followed).filter(follows.follower == current_user.username).order_by(
        input_message.post_id.desc()).all()

    number = len(results)

    if maxpage < number:
        for x in range(minpage + 4, minpage - 1, -1):
            name = results[x].poster
            myresult = personal.query.filter(personal.username == name).first()
            id.append(results[x].post_id)
            user.append(results[x].poster)
            text.append(results[x].post_text)
            time.append(results[x].post_time)
            comment.append(results[x].comment_num)
            retrant.append(results[x].retrant_num)
            upvote.append(results[x].upvote_num)
            ifretrant.append(results[x].if_retrant)
            retrantposter.append(results[x].retrant_poster)
            retranttext.append(results[x].retrant_text)
            name = results[x].poster
            myresult = personal.query.filter(personal.username == name).first()
            if myresult:
                if myresult.avatar is not None:
                    avatar.append(myresult.avatar)
                else:
                    avatar.append('user.png')
            else:
                avatar.append('user.png')
    else:
        for x in range(number - 1, minpage - 1, -1):
            id.append(results[x].post_id)
            user.append(results[x].poster)
            text.append(results[x].post_text)
            time.append(results[x].post_time)
            comment.append(results[x].comment_num)
            retrant.append(results[x].retrant_num)
            upvote.append(results[x].upvote_num)
            ifretrant.append(results[x].if_retrant)
            retrantposter.append(results[x].retrant_poster)
            retranttext.append(results[x].retrant_text)
            name = results[x].poster
            myresult = personal.query.filter(personal.username == name).first()
            if myresult:
                if myresult.avatar is not None:
                    avatar.append(myresult.avatar)
                else:
                    avatar.append('user.png')
            else:
                avatar.append('user.png')

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
    data['avatar'] = avatar
    data['current_user'] = current_avatar

    return jsonify(data)


@message_api.route('/message_myown', methods=['GET', 'POST'])
def message_myown():
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
    avatar = []

    page = int(request.args.get('page_num'))
    minpage = 5 * page
    maxpage = 5 * (page + 1)

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    profilephoto = personal.query.filter(personal.username == current_user.username).first()
    if profilephoto:
        if profilephoto.avatar is not None:
            current_avatar = profilephoto.avatar
        else:
            current_avatar = 'user.png'
    else:
        current_avatar = 'user.png'

    results = input_message.query.filter(
        input_message.poster == current_user.username).order_by(
        input_message.post_id.desc()).all()

    number = len(results)

    if maxpage < number:
        for x in range(minpage + 4, minpage - 1, -1):
            id.append(results[x].post_id)
            user.append(results[x].poster)
            text.append(results[x].post_text)
            time.append(results[x].post_time)
            comment.append(results[x].comment_num)
            retrant.append(results[x].retrant_num)
            upvote.append(results[x].upvote_num)
            ifretrant.append(results[x].if_retrant)
            retrantposter.append(results[x].retrant_poster)
            retranttext.append(results[x].retrant_text)
            name = results[x].poster
            myresult = personal.query.filter(personal.username == name).first()
            if myresult:
                if myresult.avatar is not None:
                    avatar.append(myresult.avatar)
                else:
                    avatar.append('user.png')
            else:
                avatar.append('user.png')

    else:
        for x in range(number - 1, minpage - 1, -1):
            id.append(results[x].post_id)
            user.append(results[x].poster)
            text.append(results[x].post_text)
            time.append(results[x].post_time)
            comment.append(results[x].comment_num)
            retrant.append(results[x].retrant_num)
            upvote.append(results[x].upvote_num)
            ifretrant.append(results[x].if_retrant)
            retrantposter.append(results[x].retrant_poster)
            retranttext.append(results[x].retrant_text)
            name = results[x].poster
            myresult = personal.query.filter(personal.username == name).first()
            if myresult:
                if myresult.avatar is not None:
                    avatar.append(myresult.avatar)
                else:
                    avatar.append('user.png')
            else:
                avatar.append('user.png')

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
    data['avatar'] = avatar
    data['current_user'] = current_avatar

    return jsonify(data)


# 用于展示用户评论
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
    avatar = []

    results = comments.query.filter(comments.post_id == mypost).all()

    for result in results:
        id.append(result.comment_id)
        commenter.append(result.commenter)
        text.append(result.comment_text)
        time.append(result.comment_time)
        name = result.commenter
        profilephoto = personal.query.filter(personal.username == name).first()
        if profilephoto:
            if profilephoto.avatar is not None:
                avatar.append(profilephoto.avatar)
            else:
                avatar.append('user.png')
        else:
            avatar.append('user.png')

    data['co_id'] = id
    data['co_post'] = mypost
    data['co_commenter'] = commenter
    data['co_text'] = text
    data['co_time'] = time
    data['co_page'] = page
    data['avatar'] = avatar

    return jsonify(data)


# 用于用户评论动态
@message_api.route('/to_comment', methods=['GET', 'POST'])
def to_comment():
    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputcomment = request.args.get('input_comment')
    inputpost = request.args.get('input_post')

    result = session.query(func.count(comments.comment_id).label("comment_id")).first()

    my_input_comment = comments()
    my_input_comment.comment_id = result.comment_id
    my_input_comment.post_id = inputpost
    my_input_comment.commenter = current_user.username
    my_input_comment.comment_text = inputcomment
    my_input_comment.comment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 向被评论者发送消息
    result = input_message.query.filter_by(post_id=inputpost).first()
    message_content = '评论了您'
    message_text = inputcomment + '@' + result.poster + ':' + result.post_text
    information = personal_information()
    information.receiver = result.poster
    information.sender = current_user.username
    information.message_content = message_content
    information.message_text = message_text
    information.time = Time.strftime('%Y-%m-%d %H:%M:%S', Time.localtime(Time.time()))
    information.state = 'N'
    db.session.add(information)

    db.session.add(my_input_comment)
    db.session.commit()

    postresult = input_message.query.filter_by(post_id=inputpost).first()
    newdata = postresult.comment_num + 1
    input_message.query.filter_by(post_id=inputpost).update({'comment_num': newdata})
    db.session.commit()

    data = newdata

    return jsonify(data)


# 用于点赞
@message_api.route('/to_upvote', methods=['GET', 'POST'])
def to_upvote():
    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputpost = request.args.get('input_post')

    postresult = input_message.query.filter_by(post_id=inputpost).first()
    newdata = postresult.upvote_num + 1
    input_message.query.filter_by(post_id=inputpost).update({'upvote_num': newdata})

    # 向被点赞者发送消息
    result = input_message.query.filter_by(post_id=inputpost).first()
    message_content = '赞了您的动态'
    message_text = '@' + result.poster + ':' + result.post_text
    information = personal_information()
    information.receiver = result.poster
    information.sender = current_user.username
    information.message_content = message_content
    information.message_text = message_text
    information.time = Time.strftime('%Y-%m-%d %H:%M:%S', Time.localtime(Time.time()))
    information.state = 'N'
    db.session.add(information)
    db.session.commit()

    data = newdata

    return jsonify(data)


# 用于判断是否关注
@message_api.route('/query_follow', methods=['GET', 'POST'])
def query_follow():
    thisposter = request.args.get('myposter')
    thisuser = current_user.username

    if thisposter == thisuser:
        data = 2
    else:
        result = follows.query.filter_by(follower=thisuser, followed=thisposter).first()
        if result:
            data = 1
        else:
            data = 0

    return jsonify(data)


# 用于关注
@message_api.route('/to_follow', methods=['GET', 'POST'])
def to_follow():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    inputpost = request.form.get('input_post')
    result = input_message.query.filter_by(post_id=inputpost).first()

    my_input_follow = follows()
    # 被关注
    my_input_follow.followed = result.poster
    # 关注者
    my_input_follow.follower = current_user.username

    # 向被关注者发送消息
    information = personal_information()
    information.receiver = result.poster
    information.sender = current_user.username
    information.message_content = '关注了您'
    information.message_text = '又有新粉丝啦！'
    information.time = Time.strftime('%Y-%m-%d %H:%M:%S', Time.localtime(Time.time()))
    information.state = 'N'
    db.session.add(information)

    db.session.add(my_input_follow)
    db.session.commit()

    data['value'] = 'success'

    return jsonify(data)


# 用于取消关注
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


# 用于转发动态
@message_api.route('/to_retrant', methods=['GET', 'POST'])
def to_retrant():
    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    getid = request.args.get('get_id')
    gettext = request.args.get('get_text')

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

    # 向被转发者发送消息
    result = input_message.query.filter_by(post_id=getid).first()
    message_content = '转发了您的动态'
    message_text = gettext + '@' + result.poster + ':' + result.post_text
    information = personal_information()
    information.receiver = result.poster
    information.sender = current_user.username
    information.message_content = message_content
    information.message_text = message_text
    information.time = Time.strftime('%Y-%m-%d %H:%M:%S', Time.localtime(Time.time()))
    information.state = 'N'
    db.session.add(information)
    db.session.commit()

    data = newdata

    return jsonify(data)


# 用于回复评论
@message_api.route('/to_reply', methods=['GET', 'POST'])
def to_reply():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    getid = request.form.get('get_id')
    gettext = request.form.get('get_text')

    myresult = comments.query.filter_by(comment_id=getid).first()

    inputpostid = myresult.post_id
    inputreplied = myresult.commenter

    result = session.query(func.count(comment_reply.reply_id).label("reply_id")).first()

    my_input = comment_reply()

    my_input.reply_id = result.reply_id
    my_input.comment_id = getid
    my_input.post_id = inputpostid
    my_input.replier = current_user.username
    my_input.replied = inputreplied
    my_input.reply_text = gettext
    my_input.reply_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.session.add(my_input)

    # 向被回复者发送消息
    result = comments.query.filter_by(comment_id=getid).first()
    message_content = '回复了您的评论'
    message_text = gettext + '@' + result.commenter + ':' + result.comment_text
    information = personal_information()
    information.receiver = result.commenter
    information.sender = current_user.username
    information.message_content = message_content
    information.message_text = message_text
    information.time = Time.strftime('%Y-%m-%d %H:%M:%S', Time.localtime(Time.time()))
    information.state = 'N'
    db.session.add(information)

    db.session.commit()

    data['value'] = 'success'

    return jsonify(data)


# 用于展示回复
@message_api.route('/query_reply', methods=['GET', 'POST'])
def query_reply():
    data = {}

    mycomment = int(request.args.get('mycomment'))

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    replyid = []
    replier = []
    replied = []
    text = []
    time = []

    results = comment_reply.query.filter(comment_reply.comment_id == mycomment).all()

    for result in results:
        replyid.append(result.reply_id)
        replier.append(result.replier)
        replied.append(result.replied)
        text.append(result.reply_text)
        time.append(result.reply_time)

    data['re_id'] = replyid
    data['replier'] = replier
    data['replied'] = replied
    data['re_text'] = text
    data['re_time'] = time

    return jsonify(data)


# 模板获取头像
@message_api.route('/query_avatar', methods=['GET', 'POST'])
def query_avatar():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    result = personal.query.filter(personal.username == current_user.username).first()
    if result:
        if result.avatar is not None:
            avatar = result.avatar
        else:
            avatar = 'user.png'
    else:
        avatar = 'user.png'

    data['avatar'] = avatar

    return jsonify(data)


# 用于上传头像
@message_api.route('/to_upload', methods=['GET', 'POST'])
def to_upload():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    result = personal.query.filter_by(username=current_user.username).first()
    if result:
        newdata = current_user.username + ".jpg"
        personal.query.filter(personal.username == current_user.username).update({'avatar': newdata})

    else:
        my_input_avatar = personal()
        my_input_avatar.username = current_user.username
        my_input_avatar.avatar = current_user.username + ".jpg"
        db.session.add(my_input_avatar)

    db.session.commit()
    data['value'] = 'success'
    return jsonify(data)


@message_api.route('/query_person', methods=['GET', 'POST'])
def query_person():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    result = personal.query.filter(personal.username == current_user.username).first()

    if result:
        if result.avatar is not None:
            username = result.username
            phone = result.phonenumber
            mail = result.mail
            address = result.address
            introduce = result.introduce
            avatar = result.avatar
        else:
            username = result.username
            phone = result.phonenumber
            mail = result.mail
            address = result.address
            introduce = result.introduce
            avatar = 'user.png'
    else:
        username = current_user.username
        phone = ''
        mail = ''
        address = ''
        introduce = ''
        avatar = 'user.png'

    data['usersname'] = username
    data['phone'] = phone
    data['mail'] = mail
    data['address'] = address
    data['introduce'] = introduce
    data['avatar'] = avatar

    return jsonify(data)


@message_api.route('/to_submit', methods=['GET', 'POST'])
def to_submit():
    data = {}

    myaddress = request.form.get('input_address')
    myphone = request.form.get('input_number')
    mymail = request.form.get('input_mail')
    myintroduce = request.form.get('input_introduce')

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    result = personal.query.filter_by(username=current_user.username).first()
    if result:
        newaddress = myaddress
        newphone = myphone
        newmail = mymail
        newperson = myintroduce
        personal.query.filter(personal.username == current_user.username).update({'phonenumber': newphone});
        personal.query.filter(personal.username == current_user.username).update({'mail': newmail});
        personal.query.filter(personal.username == current_user.username).update({'address': newaddress});
        personal.query.filter(personal.username == current_user.username).update({'introduce': newperson});

    else:
        my_input_information = personal()
        my_input_information.username = current_user.username
        my_input_information.address = myaddress
        my_input_information.phonenumber = myphone
        my_input_information.mail = mymail
        my_input_information.introduce = myintroduce
        db.session.add(my_input_information)

    db.session.commit()
    data['value'] = 'success'
    return jsonify(data)


# 用于设置消息私信已读未读
@message_api.route('/read_message', methods=['GET', 'POST'])
def read_message():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    info_id = request.args.get('info_id')

    result = personal_information.query.filter_by(id=info_id).first()

    result.state = 'Y'

    db.session.add(result)
    db.session.commit()

    data['value'] = info_id

    return jsonify(data)


# 判断用户名是否合法
@message_api.route('/is_username', methods=['GET', 'POST'])
def is_username():
    data = {}

    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()

    username = request.args.get('username')

    result = users.query.filter_by(username=username).first()
    if result:
        data['exit'] = 'true'
    else:
        data['exit'] = 'flase'

    return jsonify(data)


# 用于用户发私信$$管理员群发消息
@message_api.route('/send_message', methods=['GET', 'POST'])
def send_message():
    data = {}
    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    username_list = request.form.getlist('username_list[]')
    message_text = request.form.get('message_text')

    # 发送消息
    for username in username_list:
        information = personal_information()
        information.receiver = username
        information.sender = current_user.username
        information.message_text = message_text
        information.message_content = ':'
        information.time = Time.strftime('%Y-%m-%d %H:%M:%S', Time.localtime(Time.time()))
        information.state = 'N'
        db.session.add(information)

    db.session.commit()
    data['name'] = username_list
    return jsonify(data)


# 用于获取用户身份
@message_api.route('/get_role', methods=['GET', 'POST'])
def get_role():
    data = {}
    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    result = users_roles.query.filter_by(user_name=current_user.username).first()
    data['role'] = result.permissions
    return jsonify(data)


# 用于获取用户名列表
@message_api.route('/get_user_list', methods=['GET', 'POST'])
def get_user_list():
    data = {}
    db_engine = create_engine('mysql://root:0000@localhost/my_message?charset=utf8')
    Session = sessionmaker(bind=db_engine)

    user_list = []
    results = users.query.all()
    for result in results:
        user_list.append(result.username)
    data['user_list'] = user_list
    return jsonify(data)


# 用于获取用户未读信息数目
@message_api.route('/get_message_count', methods=['GET', 'POST'])
def get_message_count():
    data = {}
    results = personal_information.query.filter(personal_information.sender != 'system', ).filter_by(
        receiver=current_user.username, state='N').count()
    data['count'] = results
    return jsonify(data)

# bug
@message_api.route('/get_system_message_count', methods=['GET', 'POST'])
def get_system_message_count():
    data = {}
    results = personal_information.query.filter_by(receiver=current_user.username, sender='system', state='N').count()
    data['count'] = results
    return jsonify(data)


@message_api.route('/get_system_message', methods=['GET', 'POST'])
def get_system_message():
    result = []
    data = personal_information.query.filter_by(receiver=current_user.username, sender='system').order_by(
        desc(personal_information.time)).all()
    if data == {}:
        return jsonify(result)
    for each in data:
        result.append({"id": each.id, "message": each.message_text, "time": each.time,
                       "state": each.state})
    return jsonify(result)


@message_api.route('/read_system_message', methods=['GET', 'POST'])
def read_system_message():
    id = request.args.get('id')
    data = personal_information.query.filter_by(id=id).update({'state': 'Y'})
    db.session.commit()
    return jsonify({"result": "success"})
