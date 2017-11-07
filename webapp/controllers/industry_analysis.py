# coding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request
from os import path
from webapp.models import *
from webapp.forms import cns_filterForm1, cns_filterForm2, cns_filterForm3, cns_filterForm4, year_Form
from webapp.forms import CodeForm, invest_updateForm
from flask_login import login_required, current_user
from webapp.extensions import finance_analyst_permission
from sqlalchemy import *
# from sqlalchemy import create_engine,or_,func,desc,distinct,asc,desc,update,and_ #me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me
import MySQLdb, time, datetime, re  # re用于判断是否含中文

industryanalysis_blueprint = Blueprint(
    'industry_analysis',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'industry_analysis'),
    url_prefix="/industry_analysis"
)


@industryanalysis_blueprint.route('/industry_status', methods=('GET', 'POST'))
@industryanalysis_blueprint.route('/industry_status/<int:parameter>', methods=('GET', 'POST'))  # string,int不一样
@login_required
def industry_status(industry_gicscode_1="15", industry_gicscode_2="1510", industry_gicscode_3="151010",
                    industry_gicscode_4="25102010", parameter=4):  # 默认显示第四级分类
    parameter = parameter
    cns_filterform1 = cns_filterForm1()
    cns_filterform2 = cns_filterForm2()
    cns_filterform3 = cns_filterForm3()
    cns_filterform4 = cns_filterForm4()
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    year_list = session.query(distinct(finance_basics_add.the_year)).all()
    rs = None  # 结果集初始为None，为什么
    if parameter == 1:
        if cns_filterform1.validate_on_submit():
            industry_gicscode_1 = cns_filterform1.gics_code.data
        else:
            industry_gicscode_1 = industry_gicscode_1
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_department_industry.industry_gics_1.label("industry_gics_1")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
            cns_department_industry.industry_gicscode_1 == industry_gicscode_1).group_by(
            finance_basics_add.the_year).all()
    if parameter == 2:
        if cns_filterform2.validate_on_submit():
            industry_gicscode_2 = cns_filterform2.gics_code.data
        else:
            industry_gicscode_2 = industry_gicscode_2
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_group_industry.industry_gics_2.label("industry_gics_2")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_group_industry.industry_gicscode_2 == industry_gicscode_2).group_by(finance_basics_add.the_year).all()
    if parameter == 3:
        if cns_filterform3.validate_on_submit():
            industry_gicscode_3 = cns_filterform3.gics_code.data
        else:
            industry_gicscode_3 = industry_gicscode_3
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_industry.industry_gics_3.label("industry_gics_3")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.industry_gicscode_3 == industry_gicscode_3).group_by(finance_basics_add.the_year).all()
    if parameter == 4:
        if cns_filterform4.validate_on_submit():
            industry_gicscode_4 = cns_filterform4.gics_code.data
        else:
            industry_gicscode_4 = industry_gicscode_4
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_sub_industry.industry_gicscode_4,
                           cns_sub_industry.industry_gics_4.label("industry_gics_4")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.industry_gicscode_4 == industry_gicscode_4).group_by(finance_basics_add.the_year).all()
    # 计算rs的长度
    rs_list = range(len(rs))
    rs_list.reverse()
    return render_template("industry_analysis/industry_status.html", parameter=parameter,
                           cns_filterform1=cns_filterform1, cns_filterform2=cns_filterform2,
                           cns_filterform3=cns_filterform3, cns_filterform4=cns_filterform4, year_list=year_list, rs=rs,
                           rs_list=rs_list)


# ----cns 大陆市场----
@industryanalysis_blueprint.route('/cns_home', methods=('GET', 'POST'))
@industryanalysis_blueprint.route('/cns_home/<string:trade_code>', methods=('GET', 'POST'))
@login_required
def cns_home():
    cns_filterform1 = cns_filterForm1()
    cns_filterform2 = cns_filterForm2()
    cns_filterform3 = cns_filterForm3()
    cns_filterform4 = cns_filterForm4()
    page = request.args.get('page', 1, type=int)
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
        cns_stock_industry.trade_code).paginate(page, per_page=200, error_out=False)  # 共有3197条记录 此为分页功能
    result = pagination.items
    length = len(result)
    # filter(cns_department_industry.industry_gicscode_1=='10') 筛选行业类别OK
    v_stock_industry = cns_stock_industry.query.all()  # 以下是获取数据总共有多少个
    # stock_length = len(v_stock_industry)
    return render_template("industry_analysis/industry_classify.html", cns_filterform1=cns_filterform1,
                           cns_filterform2=cns_filterform2, cns_filterform3=cns_filterform3,
                           cns_filterform4=cns_filterform4, result=result, pagination=pagination,
                           v_stock_industry=v_stock_industry, length=length)


# ----cns行业筛选----
@industryanalysis_blueprint.route('/cns_filter/', methods=('GET', 'POST'))
@login_required
def cns_filter():
    cns_filterform1 = cns_filterForm1()
    cns_filterform2 = cns_filterForm2()
    cns_filterform3 = cns_filterForm3()
    cns_filterform4 = cns_filterForm4()
    if cns_filterform1.validate_on_submit():
        gics_code = request.form.get('gics_code')
        # industry_gics_1 = request.form.get('industry_gics_1')
        page = request.args.get('page', 1, type=int)
        pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
            cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
            cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
            cns_department_industry.industry_gics_1).join(zhengjianhui_1).add_columns(
            zhengjianhui_1.industry_CSRC12).filter(
            cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_department_industry.industry_gicscode_1 == gics_code).order_by(cns_stock_industry.trade_code).paginate(
            page, per_page=200, error_out=False)  # 300改为200
        result = pagination.items
        length = len(result)
        return render_template("industry_analysis/industry_classify_filter.html", result=result, pagination=pagination,
                               length=length, cns_filterform1=cns_filterform1, cns_filterform2=cns_filterform2,
                               cns_filterform3=cns_filterform3, cns_filterform4=cns_filterform4)
    if cns_filterform2.validate_on_submit():
        gics_code = request.form.get('gics_code')
        page = request.args.get('page', 1, type=int)
        pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
            cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
            cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
            cns_department_industry.industry_gics_1).join(zhengjianhui_1).add_columns(
            zhengjianhui_1.industry_CSRC12).filter(
            cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_group_industry.industry_gicscode_2 == gics_code).order_by(cns_stock_industry.trade_code).paginate(page,
                                                                                                                  per_page=200,
                                                                                                                  error_out=False)  # 300改为200
        result = pagination.items
        length = len(result)
        return render_template("industry_analysis/industry_classify_filter.html", result=result, pagination=pagination,
                               length=length, cns_filterform1=cns_filterform1, cns_filterform2=cns_filterform2,
                               cns_filterform3=cns_filterform3, cns_filterform4=cns_filterform4)
    if cns_filterform3.validate_on_submit():
        gics_code = request.form.get('gics_code')
        page = request.args.get('page', 1, type=int)
        pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
            cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
            cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
            cns_department_industry.industry_gics_1).join(zhengjianhui_1).add_columns(
            zhengjianhui_1.industry_CSRC12).filter(
            cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_industry.industry_gicscode_3 == gics_code).order_by(cns_stock_industry.trade_code).paginate(page,
                                                                                                            per_page=200,
                                                                                                            error_out=False)  # 300改为200
        result = pagination.items
        length = len(result)
        return render_template("industry_analysis/industry_classify_filter.html", result=result, pagination=pagination,
                               length=length, cns_filterform1=cns_filterform1, cns_filterform2=cns_filterform2,
                               cns_filterform3=cns_filterform3, cns_filterform4=cns_filterform4)
    if cns_filterform4.validate_on_submit():
        gics_code = request.form.get('gics_code')
        page = request.args.get('page', 1, type=int)
        pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
            cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
            cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
            cns_department_industry.industry_gics_1).join(zhengjianhui_1).add_columns(
            zhengjianhui_1.industry_CSRC12).filter(
            cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.industry_gicscode_4 == gics_code).order_by(cns_stock_industry.trade_code).paginate(page,
                                                                                                                per_page=200,
                                                                                                                error_out=False)  # 300改为200
        result = pagination.items
        length = len(result)
        return render_template("industry_analysis/industry_classify_filter.html", result=result, pagination=pagination,
                               length=length, cns_filterform1=cns_filterform1, cns_filterform2=cns_filterform2,
                               cns_filterform3=cns_filterform3, cns_filterform4=cns_filterform4)
    return render_template("404.html")  # 或许可用if-elif来改写一下


@industryanalysis_blueprint.route('/annual_table', methods=('GET', 'POST'))
@login_required
def annual_table(year='20151231'):
    year_form = year_Form()
    # rs=session.query(finance_basics_add,cns_department_industry.industry_gics_1,cns_group_industry.industry_gics_2,cns_industry.industry_gics_3,cns_sub_industry.industry_gics_4).filter(finance_basics_add.the_year=="20151231").filter(finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(cns_industry.belong==cns_group_industry.industry_gicscode_2).filter(cns_group_industry.belong==cns_department_industry.industry_gicscode_1).all()
    if year_form.validate_on_submit():
        year_get = request.form.get('year')
        year = year_get + '1231'  # 做成如 20161231
    page = request.args.get('page', 1, type=int)
    pagination = finance_basics_add.query.filter(finance_basics_add.the_year == year).order_by(
        finance_basics_add.trade_code).paginate(page, per_page=200, error_out=False)
    rs = pagination.items
    length = len(rs)
    return render_template("industry_analysis/annual_table.html", year=year, year_form=year_form, rs=rs,
                           pagination=pagination, length=length)


@industryanalysis_blueprint.route('/annual_table_b', methods=('GET', 'POST'))  # 太慢了！！！
@industryanalysis_blueprint.route('/annual_table_b/<int:parameter>', methods=('GET', 'POST'))
@login_required
def annual_table_b(year='20151231', parameter=4):  # 默认是2015年
    parameter = parameter
    year_form = year_Form()
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    # rs_all是将财务指标指定年份全部累和
    rs_all = session.query(func.sum(finance_basics_add.tot_oper_rev).label("all_tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("all_net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("all_wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("all_tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("all_tot_liab"),
                           func.sum(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label(
                               "all_net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("all_wgsd_com_eq")).filter(
        finance_basics_add.the_year == year).all()
    if parameter == 1:
        if year_form.validate_on_submit():
            year_get = request.form.get('year')
            year = year_get + '1231'
        else:
            year = year
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.max(finance_basics_add.tot_oper_rev).label("mx_tot_oper_rev"),
                           func.max(finance_basics_add.net_profit_is).label("mx_net_profit_is"),
                           func.max(finance_basics_add.wgsd_net_inc).label("mx_wgsd_net_inc"),
                           func.max(finance_basics_add.tot_assets).label("mx_tot_assets"),
                           func.max(finance_basics_add.tot_liab).label("mx_tot_liab"),
                           func.max(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("mx_net_assets"),
                           func.max(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_department_industry.industry_gicscode_1.label("industry_gicscode_1"),
                           cns_department_industry.industry_gics_1.label("industry_gics_1")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            cns_group_industry.belong == cns_department_industry.industry_gicscode_1).filter(
            finance_basics_add.the_year == year).group_by(cns_department_industry.industry_gicscode_1).all()
        length = len(rs)
    if parameter == 2:
        if year_form.validate_on_submit():
            year_get = request.form.get('year')
            year = year_get + '1231'
        else:
            year = year
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.max(finance_basics_add.tot_oper_rev).label("mx_tot_oper_rev"),
                           func.max(finance_basics_add.net_profit_is).label("mx_net_profit_is"),
                           func.max(finance_basics_add.wgsd_net_inc).label("mx_wgsd_net_inc"),
                           func.max(finance_basics_add.tot_assets).label("mx_tot_assets"),
                           func.max(finance_basics_add.tot_liab).label("mx_tot_liab"),
                           func.max(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("mx_net_assets"),
                           func.max(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_group_industry.industry_gicscode_2.label("industry_gicscode_2"),
                           cns_group_industry.industry_gics_2.label("industry_gics_2")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            cns_industry.belong == cns_group_industry.industry_gicscode_2).filter(
            finance_basics_add.the_year == year).group_by(cns_group_industry.industry_gicscode_2).all()
        length = len(rs)
    if parameter == 3:
        if year_form.validate_on_submit():
            year_get = request.form.get('year')
            year = year_get + '1231'
        else:
            year = year
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.max(finance_basics_add.tot_oper_rev).label("mx_tot_oper_rev"),
                           func.max(finance_basics_add.net_profit_is).label("mx_net_profit_is"),
                           func.max(finance_basics_add.wgsd_net_inc).label("mx_wgsd_net_inc"),
                           func.max(finance_basics_add.tot_assets).label("mx_tot_assets"),
                           func.max(finance_basics_add.tot_liab).label("mx_tot_liab"),
                           func.max(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("mx_net_assets"),
                           func.max(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_industry.industry_gicscode_3.label("industry_gicscode_3"),
                           cns_industry.industry_gics_3.label("industry_gics_3")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            cns_sub_industry.belong == cns_industry.industry_gicscode_3).filter(
            finance_basics_add.the_year == year).group_by(cns_industry.industry_gicscode_3).all()
        length = len(rs)
    if parameter == 4:
        if year_form.validate_on_submit():
            year_get = request.form.get('year')
            year = year_get + '1231'  # 做成如 20161231
        else:
            year = year
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.max(finance_basics_add.tot_oper_rev).label("mx_tot_oper_rev"),
                           func.max(finance_basics_add.net_profit_is).label("mx_net_profit_is"),
                           func.max(finance_basics_add.wgsd_net_inc).label("mx_wgsd_net_inc"),
                           func.max(finance_basics_add.tot_assets).label("mx_tot_assets"),
                           func.max(finance_basics_add.tot_liab).label("mx_tot_liab"),
                           func.max(finance_basics_add.tot_assets - finance_basics_add.tot_liab).label("mx_net_assets"),
                           func.max(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           cns_sub_industry.industry_gicscode_4.label("industry_gicscode_4"),
                           cns_sub_industry.industry_gics_4.label("industry_gics_4")).filter(
            finance_basics_add.trade_code == cns_stock_industry.trade_code).filter(
            cns_stock_industry.industry_gicscode_4 == cns_sub_industry.industry_gicscode_4).filter(
            finance_basics_add.the_year == year).group_by(cns_sub_industry.industry_gicscode_4).all()
        length = len(rs)
    # 分组后，计算7个财务指标的组最大值
    list_tot_oper_rev = []
    for x in range(length):
        list_tot_oper_rev.append(rs[x].tot_oper_rev)
    max_tot_oper_rev = max(list_tot_oper_rev)
    list_net_profit_is = []
    for x in range(length):
        list_net_profit_is.append(rs[x].net_profit_is)
    max_net_profit_is = max(list_net_profit_is)
    list_wgsd_net_inc = []
    for x in range(length):
        list_wgsd_net_inc.append(rs[x].wgsd_net_inc)
    max_wgsd_net_inc = max(list_wgsd_net_inc)
    list_tot_assets = []
    for x in range(length):
        list_tot_assets.append(rs[x].tot_assets)
    max_tot_assets = max(list_tot_assets)
    list_tot_liab = []
    for x in range(length):
        list_tot_liab.append(rs[x].tot_liab)
    max_tot_liab = max(list_tot_liab)
    list_net_assets = []
    for x in range(length):
        list_net_assets.append(rs[x].net_assets)
    max_net_assets = max(list_net_assets)
    list_wgsd_com_eq = []
    for x in range(length):
        list_wgsd_com_eq.append(rs[x].wgsd_com_eq)
    max_wgsd_com_eq = max(list_wgsd_com_eq)
    return render_template("industry_analysis/annual_table_b.html", parameter=parameter, year=year, year_form=year_form,
                           rs=rs, rs_all=rs_all, length=length, max_tot_oper_rev=max_tot_oper_rev,
                           max_net_profit_is=max_net_profit_is, max_wgsd_net_inc=max_wgsd_net_inc,
                           max_tot_assets=max_tot_assets, max_tot_liab=max_tot_liab, max_net_assets=max_net_assets,
                           max_wgsd_com_eq=max_wgsd_com_eq)


@industryanalysis_blueprint.route('/market_status', methods=('GET', 'POST'))  # 太慢了！！！
@login_required
def market_status():
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    # 做一个year_list，以万科A为标准
    year_list = []
    wanke_latest = session.query((finance_basics_add.the_year).label("the_year")).filter(
        finance_basics_add.sec_name == '万科A').order_by(finance_basics_add.the_year.desc()).first()
    year = int(wanke_latest.the_year[:4])
    n = 10  # 需要加1
    while n > 0:
        year_list.append(str(year) + '1231')
        year = year - 1
        n = n - 1
    # 结果如下：['20161231', '20151231', '20141231', '20131231', '20121231', '20111231', '20101231', '20091231', '20081231', '20071231']
    # 做一个结果集
    rs_list = []
    for year in year_list:
        rs = session.query(func.sum(finance_basics_add.tot_oper_rev).label("tot_oper_rev"),
                           func.sum(finance_basics_add.net_profit_is).label("net_profit_is"),
                           func.sum(finance_basics_add.wgsd_net_inc).label("wgsd_net_inc"),
                           func.sum(finance_basics_add.tot_assets).label("tot_assets"),
                           func.sum(finance_basics_add.tot_liab).label("tot_liab"),
                           func.sum(finance_basics_add.net_assets).label("net_assets"),
                           func.sum(finance_basics_add.wgsd_com_eq).label("wgsd_com_eq"),
                           func.sum(finance_basics_add.operatecashflow_ttm2).label("operatecashflow_ttm2"),
                           func.sum(finance_basics_add.investcashflow_ttm2).label("investcashflow_ttm2"),
                           func.sum(finance_basics_add.financecashflow_ttm2).label("financecashflow_ttm2"),
                           func.sum(finance_basics_add.cashflow_ttm2).label("cashflow_ttm2"),
                           func.sum(finance_basics_add.free_cash_flow).label("free_cash_flow"),
                           func.avg(finance_basics_add.net_profit_rate).label("net_profit_rate"),
                           func.avg(finance_basics_add.tot_assets_turnover).label("tot_assets_turnover"),
                           func.avg(finance_basics_add.equ_multi).label("equ_multi"),
                           func.avg(finance_basics_add.roe_tot).label("roe_tot"),
                           func.avg(finance_basics_add.roe_holder).label("roe_holder"),
                           func.count(finance_basics_add.trade_code).label("company_num"),
                           finance_basics_add.the_year).filter(finance_basics_add.the_year == year).first()
        rs_list.append(rs)
    return render_template('industry_analysis/market_status.html', rs_list=rs_list)

@industryanalysis_blueprint.route('/market_value', methods=('GET', 'POST'))  # 太慢了！！！
@login_required
def market_value():
    return render_template('industry_analysis/market_value.html')
