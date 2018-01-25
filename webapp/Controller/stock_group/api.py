# coding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request, session, make_response, jsonify, flash
from webapp.models import *
from sqlalchemy import create_engine,or_
from sqlalchemy.orm import sessionmaker

stockgroup_api = Blueprint(
    'stock_group_api',
    __name__,
    url_prefix="/stock_group_api"
)


@stockgroup_api.route('/cns_home', methods=('GET', 'POST'))
def get_cns_home_data():
    area = request.args.get('area')
    gic1 = request.args.get("gic1")
    gic2 = request.args.get("gic2")
    gic3 = request.args.get("gic3")
    gic4 = request.args.get("gic4")
    filters = {
        cns_stock_industry.province.like("%" + area + "%"),
        cns_department_industry.industry_gicscode_1.like(gic1),
        cns_group_industry.industry_gicscode_2.like(gic2),
        cns_industry.industry_gicscode_3.like(gic3),
        cns_sub_industry.industry_gicscode_4.like(gic4)
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    stockinfo = []
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
    stockinfos = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).filter(*filters).order_by(cns_stock_industry.trade_code).all()
    for result in stockinfos:
        stockinfo.append(
            [result[0].trade_code, result[0].sec_name, str(result[0].ipo_date), result.industry_gics_1, result.industry_gics_2,
             result.industry_gics_3, result.industry_gics_4, result[0].business, result[0].province, result[0].city,
             result[0].exch_city, result[0].country, result[0].curr, result[0].industry_CSRC12, result[0].industry_CSRC12,
             result[0].nature, result[0].hushen_300])
    return jsonify({"stockinfo":stockinfo,"pie1_data":pie1_data,"pie2_data":pie2_data,"pie3_data":pie3_data,"pie4_data":pie4_data})

@stockgroup_api.route('/hushen_300', methods=('GET', 'POST'))
def get_hushen_300_data():
    area = request.args.get('area')
    gic1 = request.args.get("gic1")
    gic2 = request.args.get("gic2")
    gic3 = request.args.get("gic3")
    gic4 = request.args.get("gic4")
    filters = {
        cns_stock_industry.province.like("%" + area + "%"),
        cns_department_industry.industry_gicscode_1.like(gic1),
        cns_group_industry.industry_gicscode_2.like(gic2),
        cns_industry.industry_gicscode_3.like(gic3),
        cns_sub_industry.industry_gicscode_4.like(gic4),
        cns_stock_industry.hushen_300 == '是'
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    stockinfo = []
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
    stockinfos = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).filter(*filters).order_by(cns_stock_industry.trade_code).all()
    for result in stockinfos:
        stockinfo.append(
            [result[0].trade_code, result[0].sec_name, str(result[0].ipo_date), result.industry_gics_1,
             result.industry_gics_2,
             result.industry_gics_3, result.industry_gics_4, result[0].business, result[0].province, result[0].city,
             result[0].exch_city, result[0].country, result[0].curr, result[0].industry_CSRC12,
             result[0].industry_CSRC12,
             result[0].nature, result[0].hushen_300])
    return jsonify({"stockinfo": stockinfo, "pie1_data": pie1_data, "pie2_data": pie2_data, "pie3_data": pie3_data,
                    "pie4_data": pie4_data})

@stockgroup_api.route('/shangzheng_50', methods=('GET', 'POST'))
def get_shangzheng_50_data():
    area = request.args.get('area')
    gic1 = request.args.get("gic1")
    gic2 = request.args.get("gic2")
    gic3 = request.args.get("gic3")
    gic4 = request.args.get("gic4")
    filters = {
        cns_stock_industry.province.like("%" + area + "%"),
        cns_department_industry.industry_gicscode_1.like(gic1),
        cns_group_industry.industry_gicscode_2.like(gic2),
        cns_industry.industry_gicscode_3.like(gic3),
        cns_sub_industry.industry_gicscode_4.like(gic4),
        cns_stock_industry.shangzheng_50 == '是'
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    stockinfo = []
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
    stockinfos = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).filter(*filters).order_by(cns_stock_industry.trade_code).all()
    for result in stockinfos:
        stockinfo.append(
            [result[0].trade_code, result[0].sec_name, str(result[0].ipo_date), result.industry_gics_1,
             result.industry_gics_2,
             result.industry_gics_3, result.industry_gics_4, result[0].business, result[0].province, result[0].city,
             result[0].exch_city, result[0].country, result[0].curr, result[0].industry_CSRC12,
             result[0].industry_CSRC12,
             result[0].nature, result[0].shangzheng_50])
    return jsonify({"stockinfo": stockinfo, "pie1_data": pie1_data, "pie2_data": pie2_data, "pie3_data": pie3_data,
                    "pie4_data": pie4_data})

@stockgroup_api.route('/lugutong', methods=('GET', 'POST'))
def get_lugutong_data():
    area = request.args.get('area')
    gic1 = request.args.get("gic1")
    gic2 = request.args.get("gic2")
    gic3 = request.args.get("gic3")
    gic4 = request.args.get("gic4")
    filters = {
        cns_stock_industry.province.like("%" + area + "%"),
        cns_department_industry.industry_gicscode_1.like(gic1),
        cns_group_industry.industry_gicscode_2.like(gic2),
        cns_industry.industry_gicscode_3.like(gic3),
        cns_sub_industry.industry_gicscode_4.like(gic4),
        or_(cns_stock_industry.SHSC == '是', cns_stock_industry.SHSC2 == '是')
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    stockinfo = []
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
    stockinfos = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).filter(*filters).order_by(cns_stock_industry.trade_code).all()
    for result in stockinfos:
        stockinfo.append(
            [result[0].trade_code, result[0].sec_name, str(result[0].ipo_date), result.industry_gics_1,
             result.industry_gics_2,
             result.industry_gics_3, result.industry_gics_4, result[0].business, result[0].province, result[0].city,
             result[0].exch_city, result[0].country, result[0].curr, result[0].industry_CSRC12,
             result[0].industry_CSRC12,
             result[0].nature])
    return jsonify({"stockinfo": stockinfo, "pie1_data": pie1_data, "pie2_data": pie2_data, "pie3_data": pie3_data,
                    "pie4_data": pie4_data})

@stockgroup_api.route('/cnsb_home', methods=('GET', 'POST'))
def get_cnsb_home_data():
    gic1 = request.args.get("gic1")
    gic2 = request.args.get("gic2")
    gic3 = request.args.get("gic3")
    gic4 = request.args.get("gic4")
    filters = {
        cnsb_department_industry.industry_gicscode_1.like(gic1),
        cnsb_group_industry.industry_gicscode_2.like(gic2),
        cnsb_industry.industry_gicscode_3.like(gic3),
        cnsb_sub_industry.industry_gicscode_4.like(gic4),
    }
    pie1_data = []
    pie2_data = []
    pie3_data = []
    pie4_data = []
    stockinfo = []
    pie1 = db.session.query(cnsb_department_industry.industry_gicscode_1, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).filter(*filters).group_by(
        cnsb_department_industry.industry_gicscode_1).all()
    pie2 = db.session.query(cnsb_group_industry.industry_gicscode_2, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).filter(*filters).group_by(
        cnsb_group_industry.industry_gicscode_2).all()

    pie3 = db.session.query(cnsb_industry.industry_gicscode_3, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).filter(*filters).group_by(
        cnsb_industry.industry_gicscode_3).all()

    pie4 = db.session.query(cnsb_sub_industry.industry_gicscode_4, db.func.count('*').label("dcount")).filter(
        cnsb_group_industry.belong == cnsb_department_industry.industry_gicscode_1).filter(
        cnsb_industry.belong == cnsb_group_industry.industry_gicscode_2).filter(
        cnsb_sub_industry.belong == cnsb_industry.industry_gicscode_3).filter(
        cnsb_stock_industry.industry_gicscode_4 == cnsb_sub_industry.industry_gicscode_4).filter(*filters).group_by(
        cnsb_sub_industry.industry_gicscode_4).all()
    for i in pie1:
        pie1_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie2:
        pie2_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie3:
        pie3_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    for i in pie4:
        pie4_data.append({'name': i[0].encode("utf-8"), 'value': i[1]})
    stockinfos = cnsb_stock_industry.query.join(cnsb_sub_industry).add_columns(cnsb_sub_industry.industry_gics_4).join(
        cnsb_industry).add_columns(cnsb_industry.industry_gics_3).join(cnsb_group_industry).add_columns(
        cnsb_group_industry.industry_gics_2).join(cnsb_department_industry).add_columns(
        cnsb_department_industry.industry_gics_1).join(zhengjianhui_b_2).add_columns(
        zhengjianhui_b_2.industry_CSRC12_2).join(zhengjianhui_b_1).add_columns(
        zhengjianhui_b_1.industry_CSRC12_1).filter(*filters).order_by(cnsb_stock_industry.trade_code).all()
    for result in stockinfos:
        stockinfo.append(
            [result[0].trade_code, result[0].sec_name, str(result[0].ipo_date), result.industry_gics_1,
             result.industry_gics_2,
             result.industry_gics_3, result.industry_gics_4, result.industry_CSRC12_1,
             result.industry_CSRC12_2])
    return jsonify({"stockinfo": stockinfo, "pie1_data": pie1_data, "pie2_data": pie2_data, "pie3_data": pie3_data,
                    "pie4_data": pie4_data})

@stockgroup_api.route("/update_gics/", methods=('GET', 'POST'))
def update_gics():
    trade_code = request.values.get("trade_code")
    gics_4 = request.values.get('gics_4')
    gics_name = request.values.get('gics_name')
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    session.query(cns_stock_industry).filter(cns_stock_industry.trade_code == trade_code).update(
        {'belong': gics_4, 'industry_gicscode_4': gics_4, 'industry_gics_4': gics_name})
    session.commit()
    return "true"


@stockgroup_api.route("/update_gicsb/", methods=('GET', 'POST'))
def update_gicsb():
    trade_code = request.values.get("trade_code")
    gics_4 = request.values.get('gics_4')
    gics_name = request.values.get('gics_name')
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    session.query(cnsb_stock_industry).filter(cnsb_stock_industry.trade_code == trade_code).update(
        {'industry_gicscode_4': gics_4, 'industry_gics_4': gics_name})
    session.commit()
    return "true"

