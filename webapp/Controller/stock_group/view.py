# coding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request  # me:request
import os
from webapp.models import *
from webapp.forms import *
from flask_login import login_required, current_user
from webapp.extensions import finance_analyst_permission
# from flask_sqlalchemy import SQLAlchemy #me
from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me
import MySQLdb, time

stockgroup_view = Blueprint(
    'stock_group',
    __name__,
    template_folder=os.path.abspath(os.path.join(os.getcwd(),'webapp','Template','stock_group')),
    url_prefix="/stock_group"
)

# 市场导航
@stockgroup_view.route('/navigation', methods=('GET', 'POST'))
@login_required
def navigation():
    return render_template('navigation.html')

# cns 大陆市场
@stockgroup_view.route('/cns_home', methods=('GET', 'POST'))
@login_required
def cns_home():
    cns_filterform1 = cns_filterForm1()  # 第一级 Wind 行业分类
    cns_filterform2 = cns_filterForm2()  # 第二级 Wind 行业分类
    cns_filterform3 = cns_filterForm3()  # 第三级 Wind 行业分类
    cns_filterform4 = cns_filterForm4()  # 第四级 Wind 行业分类
    page = request.args.get('page', 1, type=int)
    province = u""
    area = request.args.get('area', u'全国')
    if area != u"全国":
        province = area
    filters = {
        cns_stock_industry.province.like("%" + province + "%"),
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    pie1 = db.session.query(cns_department_industry.industry_gicscode_1, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_department_industry.industry_gicscode_1).filter(*filters).all()
    pie2 = db.session.query(cns_group_industry.industry_gicscode_2, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_group_industry.industry_gicscode_2).filter(*filters).all()

    pie3 = db.session.query(cns_industry.industry_gicscode_3, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_industry.industry_gicscode_3).filter(*filters).all()

    pie4 = db.session.query(cns_sub_industry.industry_gicscode_4, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_sub_industry.industry_gicscode_4).filter(*filters).all()
    for i in pie1:
        pie1_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie2:
        pie2_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie3:
        pie3_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie4:
        pie4_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).join(zhengjianhui_1).add_columns(
        zhengjianhui_1.industry_CSRC12).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).order_by(
        cns_stock_industry.trade_code).filter(*filters).paginate(page, per_page=200,
                                                                      error_out=False)  # 共有3197条记录 此为分页功能
    result = pagination.items
    length = len(result)
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    return render_template("cns/cns_stock_industry.html", cns_filterform1=cns_filterform1,
                           cns_filterform2=cns_filterform2, cns_filterform3=cns_filterform3,
                           cns_filterform4=cns_filterform4, result=result, pagination=pagination, length=length,
                           user=user, pie1_data=pie1_data, pie2_data=pie2_data, pie3_data=pie3_data,
                           pie4_data=pie4_data, province=area)

# 沪深300指数筛选
@stockgroup_view.route('/hushen_300', methods=('GET', 'POST'))
@stockgroup_view.route('/hushen_300/<string:trade_code>', methods=('GET', 'POST'))
@login_required
def hushen_300():
    page = request.args.get('page', 1, type=int)
    province = u""
    area = request.args.get('area', u'全国')
    if area != u"全国":
        province = area
    filters = {
        cns_stock_industry.province.like("%" + province + "%"),
        cns_stock_industry.hushen_300 == '是'
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    pie1 = db.session.query(cns_department_industry.industry_gicscode_1, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_department_industry.industry_gicscode_1).filter(*filters).all()
    pie2 = db.session.query(cns_group_industry.industry_gicscode_2, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_group_industry.industry_gicscode_2).filter(*filters).all()

    pie3 = db.session.query(cns_industry.industry_gicscode_3, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_industry.industry_gicscode_3).filter(*filters).all()

    pie4 = db.session.query(cns_sub_industry.industry_gicscode_4, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_sub_industry.industry_gicscode_4).filter(*filters).all()
    for i in pie1:
        pie1_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie2:
        pie2_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie3:
        pie3_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie4:
        pie4_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.hushen_300 == '是').order_by(
        cns_stock_industry.trade_code).paginate(page, per_page=300, error_out=False)  # 共有3197条记录 此为分页功能
    result = pagination.items
    length = len(result)

    v_stock_industry = cns_stock_industry.query.all()  # 以下是获取数据总共有多少个

    return render_template("stock_group/cns/cns_hushen_300.html", result=result, pagination=pagination,
                           v_stock_industry=v_stock_industry, length=length,pie1_data=pie1_data, pie2_data=pie2_data, pie3_data=pie3_data,
                           pie4_data=pie4_data, province=area)


# 上证50指数筛选
@stockgroup_view.route('/shangzheng_50', methods=('GET', 'POST'))
@stockgroup_view.route('/shangzheng_50/<string:trade_code>', methods=('GET', 'POST'))
@login_required
def shangzheng_50():
    page = request.args.get('page', 1, type=int)
    province = u""
    area = request.args.get('area', u'全国')
    if area != u"全国":
        province = area
    filters = {
        cns_stock_industry.province.like("%" + province + "%"),
        cns_stock_industry.shangzheng_50 == '是'
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    pie1 = db.session.query(cns_department_industry.industry_gicscode_1, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_department_industry.industry_gicscode_1).filter(*filters).all()
    pie2 = db.session.query(cns_group_industry.industry_gicscode_2, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_group_industry.industry_gicscode_2).filter(*filters).all()

    pie3 = db.session.query(cns_industry.industry_gicscode_3, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_industry.industry_gicscode_3).filter(*filters).all()

    pie4 = db.session.query(cns_sub_industry.industry_gicscode_4, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_sub_industry.industry_gicscode_4).filter(*filters).all()
    for i in pie1:
        pie1_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie2:
        pie2_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie3:
        pie3_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie4:
        pie4_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(*filters).order_by(
        cns_stock_industry.trade_code).paginate(page, per_page=200, error_out=False)  # 共有3197条记录 此为分页功能
    result = pagination.items
    length = len(result)

    v_stock_industry = cns_stock_industry.query.all()  # 以下是获取数据总共有多少个
    # stock_length = len(v_stock_industry)
    return render_template("stock_group/cns/cns_shangzheng_50.html", result=result, pagination=pagination,
                           v_stock_industry=v_stock_industry, length=length,pie1_data=pie1_data, pie2_data=pie2_data, pie3_data=pie3_data,
                           pie4_data=pie4_data, province=area)


# 陆股通指数筛选
@stockgroup_view.route('/lugutong', methods=('GET', 'POST'))
@stockgroup_view.route('/lugutong/<string:trade_code>', methods=('GET', 'POST'))
@login_required
# @finance_analyst_permission.require(http_exception=403)
def lugutong():
    page = request.args.get('page', 1, type=int)
    province = u""
    area = request.args.get('area', u'全国')
    if area != u"全国":
        province = area
    filters = {
        cns_stock_industry.province.like("%" + province + "%"),
        or_(cns_stock_industry.SHSC == '是',cns_stock_industry.SHSC2 == '是')
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    pie1 = db.session.query(cns_department_industry.industry_gicscode_1, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_department_industry.industry_gicscode_1).filter(*filters).all()
    pie2 = db.session.query(cns_group_industry.industry_gicscode_2, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_group_industry.industry_gicscode_2).filter(*filters).all()

    pie3 = db.session.query(cns_industry.industry_gicscode_3, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_industry.industry_gicscode_3).filter(*filters).all()

    pie4 = db.session.query(cns_sub_industry.industry_gicscode_4, db.func.count('*').label("dcount")).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(
        cns_stock_industry.belong_zhengjianhui == zhengjianhui_1.industry_CSRCcode12).group_by(
        cns_sub_industry.industry_gicscode_4).filter(*filters).all()
    for i in pie1:
        pie1_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie2:
        pie2_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie3:
        pie3_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie4:
        pie4_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).filter(
        cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
        cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
        cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
        cns_stock_industry.belong == cns_sub_industry.industry_gicscode_4).filter(*filters).order_by(
        cns_stock_industry.trade_code).paginate(page, per_page=200, error_out=False)  # 共有3197条记录 此为分页功能
    result = pagination.items
    length = len(result)
    # or_要从sqlalchemy中加载
    v_stock_industry = cns_stock_industry.query.all()  # 以下是获取数据总共有多少个
    return render_template("stock_group/cns/cns_lugutong.html", result=result, pagination=pagination,
                           v_stock_industry=v_stock_industry, length=length,pie1_data=pie1_data, pie2_data=pie2_data, pie3_data=pie3_data,
                           pie4_data=pie4_data, province=area)


# cnsb 沪深交易所B股公司
@stockgroup_view.route('/cnsb_home', methods=('GET', 'POST'))
@stockgroup_view.route('/cnsb_home/<string:trade_code>', methods=('GET', 'POST'))
@login_required
def cnsb_home():
    cnsb_filterform1 = cnsb_filterForm1()
    cnsb_filterform2 = cnsb_filterForm2()
    cnsb_filterform3 = cnsb_filterForm3()
    cnsb_filterform4 = cnsb_filterForm4()
    page = request.args.get('page', 1, type=int)
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    pie1 = db.session.query(cnsb_department_industry.industry_gicscode_1, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).group_by(
        cnsb_department_industry.industry_gicscode_1).all()
    pie2 = db.session.query(cnsb_group_industry.industry_gicscode_2, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).group_by(
        cnsb_group_industry.industry_gicscode_2).all()

    pie3 = db.session.query(cnsb_industry.industry_gicscode_3, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).group_by(
        cnsb_industry.industry_gicscode_3).all()

    pie4 = db.session.query(cnsb_sub_industry.industry_gicscode_4, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).group_by(
        cnsb_sub_industry.industry_gicscode_4).all()
    for i in pie1:
        pie1_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie2:
        pie2_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie3:
        pie3_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie4:
        pie4_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    pagination = cnsb_stock_industry.query.join(cnsb_sub_industry).add_columns(cnsb_sub_industry.industry_gics_4).join(
        cnsb_industry).add_columns(cnsb_industry.industry_gics_3).join(cnsb_group_industry).add_columns(
        cnsb_group_industry.industry_gics_2).join(cnsb_department_industry).add_columns(
        cnsb_department_industry.industry_gics_1).join(zhengjianhui_b_2).add_columns(
        zhengjianhui_b_2.industry_CSRC12_2).join(zhengjianhui_b_1).add_columns(
        zhengjianhui_b_1.industry_CSRC12_1).order_by(cnsb_stock_industry.trade_code).paginate(page, per_page=200,
                                                                                              error_out=False)  # 共有3197条记录 此为分页功能
    result = pagination.items
    length = len(result)
    user = users_roles.query.filter_by(user_name=current_user.username).first()
    return render_template("stock_group/cns/cnsb_stock_industry.html", cnsb_filterform1=cnsb_filterform1,
                           cnsb_filterform2=cnsb_filterform2, cnsb_filterform3=cnsb_filterform3,
                           cnsb_filterform4=cnsb_filterform4, result=result, pagination=pagination, length=length,
                           user=user,pie1_data=pie1_data, pie2_data=pie2_data, pie3_data=pie3_data,
                           pie4_data=pie4_data)