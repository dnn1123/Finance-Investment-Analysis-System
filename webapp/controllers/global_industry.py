#coding=utf-8
from flask import Blueprint,redirect,render_template,url_for,request
from os import path
from webapp.models import *
from webapp.forms import CodeForm,invest_updateForm
from flask_login import login_required,current_user
from webapp.extensions import finance_analyst_permission # 这个就是经济师权限
from sqlalchemy import create_engine,or_,func,desc,distinct,asc,desc,update,and_ #me func用于计数,desc用于逆序找max值
from sqlalchemy.orm import sessionmaker #me
import MySQLdb,time,datetime,re # re用于判断是否含中文
globalindustry_blueprint = Blueprint(
    'global_industry',
    __name__,
    template_folder=path.join(path.pardir,'templates','grobal_industry'),
    url_prefix="/global_industry"
)

@globalindustry_blueprint.route('/',methods=('GET','POST'))
@login_required
def basic():
    return render_template("global_industry/global_industry_basic.html")

 # rs = session.query(cns_stock_industry,stock_grade_l,investment_grade,func.max(stock_grade_l.the_year)).filter(cns_stock_industry.trade_code==stock_grade_l.trade_code).filter(stock_grade_l.investment_id==investment_grade.investment_id).group_by(cns_stock_industry.trade_code).paginate(page, per_page=200, error_out=False)

@globalindustry_blueprint.route('/cns_market',methods=('GET','POST'))
@globalindustry_blueprint.route('/cns_market/<string:query_history>/<string:trade_code>/<string:sec_name>', methods=('GET', 'POST'))
@login_required
def cns_market(sec_name=None,trade_code=None,query_history=None):
    sec_name=sec_name
    trade_code = trade_code
    query_history = query_history
    form = invest_updateForm()
    # 终于调试成功了！！！
    page = request.args.get('page', 1, type=int)
    pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(cns_department_industry.industry_gics_1).join(stock_grade_l).add_columns(stock_grade_l.grade_time).join(invest_grade).add_columns(invest_grade.grade_name).order_by(cns_stock_industry.trade_code).paginate(page, per_page=200,error_out=False)
    # 说明：共有3197条记录 此为分页功能 # 改成了3185个记录
    result = pagination.items
    length = len(result)
    history_data =None
    history_data_len=None
    if query_history == 'yes':
        history_data = stock_grade_h.query.filter_by(trade_code=trade_code).order_by(stock_grade_h.grade_time.desc()).join(invest_grade).add_columns(invest_grade.grade_name).all()
        history_data_len=len(history_data)
        sec_name=None
    return render_template("global_industry/cns_market.html",form=form,sec_name=sec_name,trade_code=trade_code,query_history=query_history,result=result, pagination=pagination, length=length,history_data=history_data,history_data_len=history_data_len)

# 修改:股票的评级
@globalindustry_blueprint.route('/invest_update/', methods=('GET', 'POST'))
# @globalindustry_blueprint.route('/invest_update/<string:sec_name>', methods=('GET', 'POST'))
@login_required
def invest_update(sec_name=None):  # 疑问：这一行是什么意思？
    if request.method == 'POST':
        grade_id = request.form.get('grade_id') # 从表单中的form.grade_id获得
        grade_time = datetime.datetime.now()
        sec_name = request.form['sec_name'] # 从form的<input>中获得
        trade_code = request.form['trade_code'] # 从form的<input>中获得
        db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
        Session = sessionmaker(bind=db_engine)
        session = Session()
        # 多个where的修改是这么写：.filter(and_(stock_grade_l.sec_name==sec_name,stock_grade_l.the_year==the_year))
        session.query(stock_grade_l).filter(stock_grade_l.sec_name==sec_name).update({"grade_time":grade_time}) #修改最新评级时间
        session.commit()
        session.query(stock_grade_l).filter(stock_grade_l.sec_name == sec_name).update({"grade_id": grade_id})
        session.commit() #修改最新评级
        insert_obj = stock_grade_h(trade_code=trade_code,sec_name=sec_name,grade_time=grade_time,grade_id=grade_id)
        session.add(insert_obj)
        session.commit()
        return redirect(url_for('.cns_market'))
        # return render_template('global_industry/test.html',investment_id=investment_id,the_year=the_year,sec_name=sec_name) #测试参数时候传过来了
    return None

@globalindustry_blueprint.route('/cns_history', methods=('GET', 'POST'))
@globalindustry_blueprint.route('/cns_history/<string:trade_code>', methods=('GET', 'POST'))
@login_required
def cns_history(trade_code=None):
    trade_code = trade_code
    rs = stock_grade_l.query.join(invest_grade).add_columns(invest_grade.investment_name).filter(stock_grade_l.trade_code == trade_code).order_by(stock_grade_l.the_year.desc()).all() # .all使得basequery变成list
    data_len = len(rs) # 查看有多少年的数据
    # v_stock_industry = cns_stock_industry.query.all() # 有用吗???
    # return redirect(url_for('.cns_market', trade_code=trade_code,rs=rs,data_len=data_len))
    page = request.args.get('page', 1, type=int)
    pagination = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(
        cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(
        cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(
        cns_department_industry.industry_gics_1).join(stock_grade_l).add_columns(func.max(stock_grade_l.the_year),
                                                                                    stock_grade_l.investment_id).join(
        invest_grade).add_columns(invest_grade.investment_name).group_by(
        cns_stock_industry.trade_code).paginate(page, per_page=200, error_out=False)
    # 说明：共有3197条记录 此为分页功能 # 改成了3185个记录
    result = pagination.items
    length = len(result)
    return render_template("global_industry/cns_market.html",result=result,length=length,trade_code=trade_code,rs=rs, data_len=data_len)

# ----美国市场----
@globalindustry_blueprint.route('/usa_market',methods=('GET','POST'))
@globalindustry_blueprint.route('/usa_market/<string:query_history>/<string:trade_code>/<string:sec_name>', methods=('GET', 'POST'))
@login_required
def usa_market(sec_name=None,trade_code=None,query_history=None):
    sec_name=sec_name
    trade_code = trade_code
    query_history = query_history
    form = invest_updateForm()
    # 终于调试成功了！！！
    page = request.args.get('page', 1, type=int)
    pagination = usa_stock_industry.query.join(usa_sub_industry).add_columns(usa_sub_industry.industry_gics_4).join(usa_industry).add_columns(usa_industry.industry_gics_3).join(usa_group_industry).add_columns(usa_group_industry.industry_gics_2).join(usa_department_industry).add_columns(usa_department_industry.industry_gics_1).join(usa_stock_grade_l).add_columns(usa_stock_grade_l.grade_time).join(invest_grade).add_columns(invest_grade.grade_name).order_by(usa_stock_industry.trade_code).paginate(page, per_page=200,error_out=False)
    # 说明：共有3197条记录 此为分页功能 # 改成了3185个记录
    result = pagination.items
    length = len(result)
    history_data =None
    history_data_len=None
    if query_history == 'yes':
        history_data = stock_grade_h.query.filter_by(trade_code=trade_code).order_by(stock_grade_h.grade_time.desc()).join(invest_grade).add_columns(invest_grade.grade_name).all()
        history_data_len=len(history_data)
        sec_name=None
    return render_template("global_industry/usa/usa_market.html",form=form,sec_name=sec_name,trade_code=trade_code,query_history=query_history,result=result, pagination=pagination, length=length,history_data=history_data,history_data_len=history_data_len)

























# 获取股票代码trade_code的list
#db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
#Session = sessionmaker(bind=db_engine)
#session = Session()
# test=session.query(stock_grade_l.trade_code).distinct(stock_grade_l.trade_code).all()
# for x in test:
# rs = stock_grade_l.query.filter(trade_code=='000001').order_by(stock_investment.the_year.desc()).first()

#  rs = session.query(stock_investment).outerjoin(investment_grade,stock_investment.investment_id==investment_grade.investment_id).filter(stock_investment.trade_code=='000001').order_by(stock_investment.the_year.desc())


# 修改投资评级
# @globalindustry_blueprint.route('/cns_market/grade_update/',methods=('GET','POST'))
# @globalindustry_blueprint.route('/cns_market/grade_update/<string:sec_name>',methods=('GET','POST'))
# def grade_update(sec_name='平安银行'):
#     form = cns_market_updateForm()
#     sec_name = sec_name
#     if request.method == 'POST':
#         # sec_name = request.form['sec_name'] 因为这行，出现400错误请求
#         investment_id = request.form['investment_id']
#         investment_grade = investment_grade.query.filter
#         db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
#         Session = sessionmaker(bind=db_engine)
#         session = Session()
#         session.query(cns_stock_industry).filter(cns_stock_industry.sec_name == sec_name).update({'investment_grade': investment_grade})  # 改为belong
#         session.commit()  # 少写了这一行，所以修改没成功
#         return redirect(url_for('.cns_market'))
#     return render_template("global_industry/grade_update.html",form=form,sec_name=sec_name)



# 先构建的子查询
# firstq = cns_stock_industry.query.join(cns_sub_industry).add_columns(cns_sub_industry.industry_gics_4).join(cns_industry).add_columns(cns_industry.industry_gics_3).join(cns_group_industry).add_columns(cns_group_industry.industry_gics_2).join(cns_department_industry).add_columns(cns_department_industry.industry_gics_1).join(stock_investment).add_columns(stock_investment.the_year).join(investment_grade).add_columns(investment_grade.investment_name).order_by(stock_investment.the_year.desc()).order_by(stock_investment.trade_code).subquery()
# 进一步查询
# rs = session.query(firstq).group_by(stmt.c.trade_code).all()

# sqlalchemy实现的子查询，返回的是sqlalchemy的query对象
# stmt = session.query(stock_investment.trade_code,stock_investment.the_year,investment_grade.investment_name).filter(stock_investment.investment_id==investment_grade.investment_id).order_by(stock_investment.the_year.desc()).order_by(stock_investment.trade_code).subquery()
# rs = session.query(stmt).group_by(stmt.c.trade_code).all()

