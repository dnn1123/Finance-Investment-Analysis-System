# coding=utf-8
from flask import Blueprint, redirect, render_template, url_for, request  # me:request
from os import path
from webapp.models import *  # me: stock_basics,finance_basics,invest_values,cns_stock_industry,cns_industry_detail
from webapp.forms import CodeForm, cns_UpdateForm, usa_UpdateForm, usa_filterForm1, usa_filterForm2, usa_filterForm3, \
    usa_filterForm4, usa_update_department_Form, departmentForm, cns_filterForm1, cns_filterForm2, cns_filterForm3, \
    cns_filterForm4, hks_filterForm1, hks_filterForm2, hks_filterForm3, hks_filterForm4
from flask_login import login_required, current_user
from webapp.extensions import finance_analyst_permission
# from flask_sqlalchemy import SQLAlchemy #me
from sqlalchemy import *  # me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker  # me
import MySQLdb, time

investenv_blueprint = Blueprint(
    'invest_env',
    __name__,
    template_folder=path.join(path.pardir, 'templates', 'invest_env'),
    url_prefix="/invest_env"
)


@investenv_blueprint.route('/cpi', methods=('GET', 'POST'))
@login_required
def cpi_why():  # 为什么为什么为什么，用cpi()就会出错？？？
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    # 先做一个year_list ['1990'-----'2017'即最新年份]
    year_list = []
    yearnow = time.strftime('%Y', time.localtime(time.time()))
    year_now = int(yearnow)
    n = year_now - 1990 + 1  # 需要加1
    while n > 0:
        year_list.append((str(year_now)))
        year_now = year_now - 1
        n = n - 1
    year_list.reverse()
    # sql方法：select * from cpi where datetime BETWEEN 'year-1-1' and 'year-12-31'
    # 做一个result_list
    # 用+号，连接字符串，注意，year必须是字符串形式的年，如‘1990’
    rs = []
    for year in year_list:
        rs_year = session.query(cpi).filter(and_(cpi.datetime >= year + "-1-1", cpi.datetime <= year + "-12-31")).all()
        rs_avg = session.query(func.avg(cpi.data).label("cpi")).filter(
            and_(cpi.datetime >= year + "-1-1", cpi.datetime <= year + "-12-31")).first()
        rs.append([year, rs_year, rs_avg])
    # 结果如：rs[0]----['1990', [1991年的cpi数据集list],这一年的平均值] 此三项构成
    length = len(rs)
    return render_template('invest_env/cpi.html', rs=rs, length=length)


@investenv_blueprint.route('/deposit_rate', methods=('GET', 'POST'))
@login_required
def deposit_rate_why():  # 为什么为什么为什么，deposit_rate()就会出错？？？
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    rs = session.query(deposit_rate).all()
    length = len(rs)
    return render_template('invest_env/deposit_rate.html', rs=rs, length=length)


# rs = session.query(lending_rate).all()

@investenv_blueprint.route('/lending_rate', methods=('GET', 'POST'))
@login_required
def lending_rate_why():  # 为什么为什么为什么，lending_rate()就会出错？？？
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    rs = session.query(lending_rate).all()
    length = len(rs)
    return render_template('invest_env/lending_rate.html', rs=rs, length=length)


@investenv_blueprint.route('/deposit_reserve_rate', methods=('GET', 'POST'))
@login_required
def deposit_reserve_rate_why():  # 为什么为什么为什么，deposit_reserve_rate()就会出错？？？
    db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
    Session = sessionmaker(bind=db_engine)
    session = Session()
    rs = session.query(deposit_reserve_rate).all()
    length = len(rs)
    return render_template('invest_env/deposit_reserve_rate.html', rs=rs, length=length)
