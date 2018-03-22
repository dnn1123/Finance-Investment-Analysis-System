# coding=utf-8
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin, UserMixin

# ORM访问数据库
db = SQLAlchemy()

roles = db.Table(
    'role_users',
    db.Column('user_name', db.String(80), db.ForeignKey('users.username')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permissions', db.Integer),
)


# class roles1(UserMixin, db.Model):
#     __tablename__ = 'role_users_copy'
#     id = db.Column(db.Integer, primary_key=True)
#     user_name = db.Column(db.String(80), db.ForeignKey('users.username'))
#     role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
#     permissions = db.Column(db.Integer)
class strategy(db.Model):
    __bind_key__ = 'quant'
    __tablename__ = 'strategy'
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(255))
    name_cn = db.Column(db.String(255))
    type = db.Column(db.String(255))
    description = db.Column(db.String(255))
    sample = db.Column(db.BLOB)


class subscriber(db.Model):
    __bind_key__ = 'quant'
    __tablename__ = 'subscriber'
    identifier = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20))
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'), )
    strategy_name = db.Column(db.String(255))
    parameter = db.Column(db.BLOB)
    status = db.Column(db.String(255))
    build_date = db.Column(db.DateTime)
    threadpid = db.Column(db.Integer)
    threadname = db.Column(db.String(255))


class users_roles(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'role1'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), db.ForeignKey('users.username'))
    permissions = db.Column(db.Integer)
    # permissions_name = db.Column(db.Integer)


# 动态
class input_message(db.Model):
    __bind_key__ = 'my_message'
    __tablename__ = 'input_message'
    post_id = db.Column(db.Integer, primary_key=True)
    poster = db.Column(db.String(20))
    post_text = db.Column(db.Text)
    post_time = db.Column(db.String(45))
    comment_num = db.Column(db.Integer)
    retrant_num = db.Column(db.Integer)
    upvote_num = db.Column(db.Integer)
    if_retrant = db.Column(db.Integer)
    retrant_poster = db.Column(db.String(20))
    retrant_text = db.Column(db.Text)


# 评论
class comments(db.Model):
    __bind_key__ = 'my_message'
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    commenter = db.Column(db.String(20))
    comment_text = db.Column(db.Text)
    comment_time = db.Column(db.String(45))


# 关注关系
class follows(db.Model):
    __bind_key__ = 'my_message'
    __tablename__ = 'follows'
    follower = db.Column(db.String(20), primary_key=True)
    followed = db.Column(db.String(20), primary_key=True)


# 回复
class comment_reply(db.Model):
    __bind_key__ = 'my_message'
    __tablename__ = 'comment_reply'
    reply_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)
    replier = db.Column(db.String(20))
    replied = db.Column(db.String(20))
    reply_text = db.Column(db.Text)
    reply_time = db.Column(db.String(45))


# 用户信息
class personal(db.Model):
    __bind_key__ = 'my_message'
    __tablename__ = 'personal'
    username = db.Column(db.String(20), primary_key=True)
    avatar = db.Column(db.String(25))
    introduce = db.Column(db.Text)
    sex = db.Column(db.String(10))


# 用户个人消息
class personal_information(db.Model):
    __bind_key__ = 'my_message'
    __tablename__ = 'personal_information'

    id = db.Column(db.Integer, primary_key=True)
    receiver = db.Column(db.String(20), db.ForeignKey('users.username'))
    sender = db.Column(db.String(20), db.ForeignKey('users.username'))
    message_content = db.Column(db.String(20))
    message_text = db.Column(db.Text)
    time = db.Column(db.String(45))
    state = db.Column(db.String(20))


# 权限常量
class Permission:
    administrator = 1
    trader = 2
    visitor = 3


# 用户余额
class user_money(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'user_money'
    user_name = db.Column(db.String(20), db.ForeignKey('users.username'), primary_key=True)
    user_money = db.Column(db.Integer())


# 会员信息
class member_information(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'member_information'
    user_name = db.Column(db.String(20), db.ForeignKey('users.username'), primary_key=True)
    member_type = db.Column(db.String(20))
    member_expiration_date = db.Column(db.DateTime)


class users(UserMixin, db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'users'
    # username = db.StringField(max_length=100, primary_key=True)
    username = db.Column(db.String(45), primary_key=True)
    password = db.Column(db.String(45))

    # def __init__(self, **kwargs):
    #     super(User, self).__init__(**kwargs)
    def can(self, permissions):
        result = users_roles.query.filter_by(user_name=self.username).first()
        return result is not None and \
               result.permissions <= permissions

    def is_administrator(self):
        return self.can(Permission.administrator)

    # roles = db.relationship(
    #         'Role',
    #         secondary=roles,
    #         backref=db.backref('users', lazy='dynamic')
    # )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return unicode(self.username)


class favorite_code(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'favorite_code'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), db.ForeignKey('users.username'))
    code = db.Column(db.String(10))


class history(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'history'
    ID = db.Column(db.Integer, primary_key=True)
    users = db.Column(db.String(20), db.ForeignKey('users.username'))
    code = db.Column(db.String(10))
    position = db.Column(db.String(10))
    price = db.Column(db.Numeric)
    amount = db.Column(db.Integer)
    commission = db.Column(db.Numeric)
    time = db.Column(db.DateTime())


class investment_portfolio(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'investment_portfolio'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(20), db.ForeignKey('users.username'))
    code = db.Column(db.String(10))
    shares = db.Column(db.Integer)
    total_cost = db.Column(db.Numeric)


class Role(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class basic_stock(db.Model):
    __tablename__ = "basic_stock"
    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(20))
    industry = db.Column(db.String(20))


class stock_basics(db.Model):
    __tablename__ = 'stock_basics'
    trade_code = db.Column(db.String(20), primary_key=True)
    sec_name = db.Column(db.String(20))
    ipo_date = db.Column(db.DateTime())
    exch_city = db.Column(db.String(20))
    industry_gics = db.Column(db.String(20))
    concept = db.Column(db.String(200))
    curr = db.Column(db.String(20))
    fiscaldate = db.Column(db.String(20))
    auditor = db.Column(db.String(200))
    province = db.Column(db.String(20))
    city = db.Column(db.String(20))
    founddate = db.Column(db.DateTime())
    nature1 = db.Column(db.String(20))
    boardchairmen = db.Column(db.String(20))
    holder_controller = db.Column(db.String(20))
    website = db.Column(db.String(10000))
    phone = db.Column(db.String(200))
    majorproducttype = db.Column(db.String(200))
    majorproductname = db.Column(db.String(2000))


class finance_basics(db.Model):
    __tablename__ = 'finance_basics'
    trade_code = db.Column(db.String(10), db.ForeignKey('cns_stock_industry.trade_code'), primary_key=True)
    sec_name = db.Column(db.String(40))
    the_year = db.Column(db.String(40), primary_key=True)
    tot_oper_rev = db.Column(db.Numeric(20, 3))
    tot_oper_cost = db.Column(db.Numeric(20, 3))
    fin_exp_is = db.Column(db.Numeric(20, 3))
    tot_profit = db.Column(db.Numeric(20, 3))
    net_profit_is = db.Column(db.Numeric(20, 3))
    wgsd_net_inc = db.Column(db.Numeric(20, 3))
    tot_assets = db.Column(db.Numeric(20, 3))
    tot_cur_assets = db.Column(db.Numeric(20, 3))
    tot_non_cur_assets = db.Column(db.Numeric(20, 3))
    tot_liab = db.Column(db.Numeric(20, 3))
    tot_cur_liab = db.Column(db.Numeric(20, 3))
    tot_non_cur_liab = db.Column(db.Numeric(20, 3))
    wgsd_com_eq = db.Column(db.Numeric(20, 3))
    operatecashflow_ttm2 = db.Column(db.Numeric(20, 3))
    investcashflow_ttm2 = db.Column(db.Numeric(20, 3))
    financecashflow_ttm2 = db.Column(db.Numeric(20, 3))
    cashflow_ttm2 = db.Column(db.Numeric(20, 3))
    monetary_cap = db.Column(db.Numeric(20, 3))
    grossprofitmargin = db.Column(db.Numeric(20, 4))
    roic = db.Column(db.Numeric(20, 4))
    turndays = db.Column(db.Numeric(20, 4))
    invturndays = db.Column(db.Numeric(20, 4))
    arturndays = db.Column(db.Numeric(20, 4))
    apturndays = db.Column(db.Numeric(20, 4))



class finance_basics_add(db.Model):
    __tablename__ = 'finance_basics_add'
    trade_code = db.Column(db.String(10), db.ForeignKey('cns_stock_industry.trade_code'), primary_key=True)
    sec_name = db.Column(db.String(40))
    the_year = db.Column(db.String(40), primary_key=True)
    tot_oper_rev = db.Column(db.Numeric(20, 3))
    tot_oper_cost = db.Column(db.Numeric(20, 3))
    fin_exp_is = db.Column(db.Numeric(20, 3))
    tot_profit = db.Column(db.Numeric(20, 3))
    net_profit_is = db.Column(db.Numeric(20, 3))
    wgsd_net_inc = db.Column(db.Numeric(20, 3))
    tot_assets = db.Column(db.Numeric(20, 3))
    tot_cur_assets = db.Column(db.Numeric(20, 3))
    tot_non_cur_assets = db.Column(db.Numeric(20, 3))
    tot_liab = db.Column(db.Numeric(20, 3))
    tot_cur_liab = db.Column(db.Numeric(20, 3))
    tot_non_cur_liab = db.Column(db.Numeric(20, 3))
    wgsd_com_eq = db.Column(db.Numeric(20, 3))
    operatecashflow_ttm2 = db.Column(db.Numeric(20, 3))
    investcashflow_ttm2 = db.Column(db.Numeric(20, 3))
    financecashflow_ttm2 = db.Column(db.Numeric(20, 3))
    cashflow_ttm2 = db.Column(db.Numeric(20, 3))
    monetary_cap = db.Column(db.Numeric(20, 3))
    grossprofitmargin = db.Column(db.Numeric(20, 4))
    roic = db.Column(db.Numeric(20, 4))
    turndays = db.Column(db.Numeric(20, 4))
    invturndays = db.Column(db.Numeric(20, 4))
    arturndays = db.Column(db.Numeric(20, 4))
    apturndays = db.Column(db.Numeric(20, 4))
    net_profit_rate = db.Column(db.Numeric(20, 4))
    tot_assets_turnover = db.Column(db.Numeric(20, 4))
    equ_multi = db.Column(db.Numeric(20, 4))
    roe_tot = db.Column(db.Numeric(20, 4))
    roe_holder = db.Column(db.Numeric(20, 4))
    net_assets = db.Column(db.Numeric(20, 4))
    free_cash_flow = db.Column(db.Numeric(20, 4))
    ebit_rate = db.Column(db.Numeric(20, 4))
    rota = db.Column(db.Numeric(20, 4))
    equ_pb = db.Column(db.Numeric(20, 6))
    equ_pe = db.Column(db.Numeric(20, 6))


class invest_values(db.Model):
    __tablename__ = 'invest_values'
    trade_code = db.Column(db.String(40), primary_key=True)
    sec_name = db.Column(db.String(40))
    the_year = db.Column(db.String(40), primary_key=True)
    total_shares = db.Column(db.Numeric(38, 6))
    div_cashandstock = db.Column(db.Numeric(38, 6))
    ev = db.Column(db.Numeric(38, 6))
    dividendyield2 = db.Column(db.Numeric(38, 8))
    ev1 = db.Column(db.Numeric(38, 6))
    ev2 = db.Column(db.Numeric(38, 6))
    employee = db.Column(db.Integer)


class cns_department_industry(db.Model):
    __tablename__ = 'cns_department_industry'
    industry_gicscode_1 = db.Column(db.String(40), primary_key=True)
    industry_gics_1 = db.Column(db.String(40))


class cns_group_industry(db.Model):
    industry_gicscode_2 = db.Column(db.String(40), primary_key=True)
    industry_gics_2 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('cns_department_industry.industry_gicscode_1'))


class cns_industry(db.Model):
    industry_gicscode_3 = db.Column(db.String(40), primary_key=True)
    industry_gics_3 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('cns_group_industry.industry_gicscode_2'))


class cns_sub_industry(db.Model):
    industry_gicscode_4 = db.Column(db.String(40), primary_key=True)
    industry_gics_4 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('cns_industry.industry_gicscode_3'))


class cns_stock_industry(db.Model):
    __tablename__ = 'cns_stock_industry'
    trade_code = db.Column(db.String(40), primary_key=True)
    sec_name = db.Column(db.String(40))
    industry_gicscode_4 = db.Column(db.String(40))
    industry_gics_4 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('cns_sub_industry.industry_gicscode_4'))
    ipo_date = db.Column(db.DateTime)
    business = db.Column(db.String(5000))
    province = db.Column(db.String(40))
    city = db.Column(db.String(40))
    exch_city = db.Column(db.String(40))
    country = db.Column(db.String(40))
    curr = db.Column(db.String(40))
    nature = db.Column(db.String(40))
    hushen_300 = db.Column(db.String(40))
    shangzheng_50 = db.Column(db.String(40))
    SHSC = db.Column(db.String(40))
    SHSC2 = db.Column(db.String(40))
    industry_CSRCcode12 = db.Column(db.String(40))
    industry_CSRC12 = db.Column(db.String(40))
    belong_zhengjianhui = db.Column(db.String(40), db.ForeignKey('zhengjianhui_1.industry_CSRCcode12'))


class stock_grade_l(db.Model):
    __tablename__ = 'stock_grade_l'
    trade_code = db.Column(db.String(40), db.ForeignKey('cns_stock_industry.trade_code'), primary_key=True)
    sec_name = db.Column(db.String(40))
    grade_time = db.Column(db.DateTime(6))
    grade_id = db.Column(db.String(40), db.ForeignKey('invest_grade.grade_id'))


class stock_grade_h(db.Model):
    __tablename__ = 'stock_grade_h'
    trade_code = db.Column(db.String(40))
    sec_name = db.Column(db.String(40))
    grade_time = db.Column(db.DateTime(6), primary_key=True)
    grade_id = db.Column(db.String(40), db.ForeignKey('invest_grade.grade_id'))


class invest_grade(db.Model):
    __tablename__ = 'invest_grade'
    grade_id = db.Column(db.String(40), primary_key=True)
    grade_name = db.Column(db.String(40))


class zhengjianhui_1(db.Model):
    __tablename__ = 'zhengjianhui_1'
    industry_CSRCcode12 = db.Column(db.String(40), primary_key=True)
    industry_CSRC12 = db.Column(db.String(40))


# zhengjianhui_2 作废：因为它distinct重复，无法变成一个二级行业分类标准
# class zhengjianhui_2(db.Model):
#     __tablename__='zhengjianhui_2'
#     trade_code = db.Column(db.String(40),primary_key=True)
#     industry_CSRCcode12 = db.Column(db.String(40))
#     industry_CSRC12 = db.Column(db.String(40))
#     belong = db.Column(db.String(40), db.ForeignKey('zhengjianhui_1.industry_CSRCcode12'))

# 大陆市场 B股
class cnsb_stock_industry(db.Model):
    __tablename__ = 'cnsb_stock_industry'
    trade_code = db.Column(db.String(40), primary_key=True)
    sec_name = db.Column(db.String(40))
    industry_gicscode_4 = db.Column(db.String(40), db.ForeignKey('cnsb_sub_industry.industry_gicscode_4'))
    industry_gics_4 = db.Column(db.String(40))
    ipo_date = db.Column(db.DateTime)
    belong_zhengjianhui = db.Column(db.String(40), db.ForeignKey('zhengjianhui_b_2.industry_CSRCcode12'))


class cnsb_department_industry(db.Model):
    __tablename__ = 'cnsb_department_industry'
    industry_gicscode_1 = db.Column(db.String(40), primary_key=True)
    industry_gics_1 = db.Column(db.String(40))


class cnsb_group_industry(db.Model):
    industry_gicscode_2 = db.Column(db.String(40), primary_key=True)
    industry_gics_2 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('cnsb_department_industry.industry_gicscode_1'))


class cnsb_industry(db.Model):
    industry_gicscode_3 = db.Column(db.String(40), primary_key=True)
    industry_gics_3 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('cnsb_group_industry.industry_gicscode_2'))


class cnsb_sub_industry(db.Model):
    industry_gicscode_4 = db.Column(db.String(40), primary_key=True)
    industry_gics_4 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('cnsb_industry.industry_gicscode_3'))


class zhengjianhui_b_1(db.Model):
    __tablename__ = 'zhengjianhui_b_1'
    industry_CSRCcode12 = db.Column(db.String(40), primary_key=True)
    industry_CSRC12_1 = db.Column(db.String(40))


class zhengjianhui_b_2(db.Model):
    __tablename__ = 'zhengjianhui_b_2'
    trade_code = db.Column(db.String(40), primary_key=True)
    industry_CSRCcode12 = db.Column(db.String(40))
    industry_CSRC12_2 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('zhengjianhui_b_1.industry_CSRCcode12'))


# 美国市场
class usa_department_industry(db.Model):
    __tablename__ = 'usa_department_industry'
    industry_gicscode_1 = db.Column(db.String(40), primary_key=True)
    industry_gics_1 = db.Column(db.String(40))


class usa_group_industry(db.Model):
    __tablename__ = 'usa_group_industry'
    industry_gicscode_2 = db.Column(db.String(40), primary_key=True)
    industry_gics_2 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('usa_department_industry.industry_gicscode_1'))


class usa_industry(db.Model):
    __tablename__ = 'usa_industry'
    industry_gicscode_3 = db.Column(db.String(40), primary_key=True)
    industry_gics_3 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('usa_group_industry.industry_gicscode_2'))


class usa_sub_industry(db.Model):
    __tablename__ = 'usa_sub_industry'
    industry_gicscode_4 = db.Column(db.String(40), primary_key=True)
    industry_gics_4 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('usa_industry.industry_gicscode_3'))


class usa_stock_industry(db.Model):
    __tablename__ = 'usa_stock_industry'
    trade_code = db.Column(db.String(40), primary_key=True)
    sec_name = db.Column(db.String(40))
    ipo_date = db.Column(db.DateTime)
    industry_gicscode_4 = db.Column(db.String(40), db.ForeignKey('usa_sub_industry.industry_gicscode_4'))
    industry_gics_4 = db.Column(db.String(40))
    business = db.Column(db.String(5000))
    address = db.Column(db.String(5000))
    exch_city = db.Column(db.String(40))
    country = db.Column(db.String(40))
    curr = db.Column(db.String(40))
    briefing = db.Column(db.String(5000))


class usa_djia(db.Model):
    __tablename__ = 'usa_djia'
    trade_code = db.Column(db.String(40), primary_key=True)
    sec_name = db.Column(db.String(40))


class usa_stock_grade_l(db.Model):
    __tablename__ = 'usa_stock_grade_l'
    trade_code = db.Column(db.String(40), db.ForeignKey('usa_stock_industry.trade_code'), primary_key=True)
    sec_name = db.Column(db.String(40))
    grade_time = db.Column(db.DateTime(6))
    grade_id = db.Column(db.String(40), db.ForeignKey('invest_grade.grade_id'))


# class usa_stock_grade_h(db.Model):
#     __tablename__='stock_grade_h'
#     trade_code = db.Column(db.String(40))
#     sec_name = db.Column(db.String(40))
#     grade_time = db.Column(db.DateTime(6),primary_key=True)
#     grade_id = db.Column(db.String(40),db.ForeignKey('invest_grade.grade_id'))



# 香港市场
class hks_department_industry(db.Model):
    __tablename__ = 'hks_department_industry'
    industry_gicscode_1 = db.Column(db.String(40), primary_key=True)
    industry_gics_1 = db.Column(db.String(40))


class hks_group_industry(db.Model):
    __tablename__ = 'hks_group_industry'
    industry_gicscode_2 = db.Column(db.String(40), primary_key=True)
    industry_gics_2 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('hks_department_industry.industry_gicscode_1'))


class hks_industry(db.Model):
    __tablename__ = 'hks_industry'
    industry_gicscode_3 = db.Column(db.String(40), primary_key=True)
    industry_gics_3 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('hks_group_industry.industry_gicscode_2'))


class hks_sub_industry(db.Model):
    __tablename__ = 'hks_sub_industry'
    industry_gicscode_4 = db.Column(db.String(40), primary_key=True)
    industry_gics_4 = db.Column(db.String(40))
    belong = db.Column(db.String(40), db.ForeignKey('hks_industry.industry_gicscode_3'))


class hks_stock_industry(db.Model):
    __tablename__ = 'hks_stock_industry'
    trade_code = db.Column(db.String(40), primary_key=True)
    sec_name = db.Column(db.String(40))
    ipo_date = db.Column(db.DateTime)
    industry_gicscode_4 = db.Column(db.String(40), db.ForeignKey('hks_sub_industry.industry_gicscode_4'))
    industry_gics_4 = db.Column(db.String(40))
    business = db.Column(db.String(5000))
    address = db.Column(db.String(5000))
    exch_city = db.Column(db.String(40))
    country = db.Column(db.String(40))
    curr = db.Column(db.String(40))
    comp_name = db.Column(db.String(5000))


class cpi(db.Model):
    __tablename__ = 'cpi'
    datetime = db.Column(db.DateTime, primary_key=True)
    data = db.Column(db.Numeric(10, 7))


class deposit_rate(db.Model):
    __tablename__ = 'deposit_rate'
    datetime = db.Column(db.DateTime, primary_key=True)
    M0009805 = db.Column(db.Numeric(6, 3))
    M0009806 = db.Column(db.Numeric(6, 3))
    M0009807 = db.Column(db.Numeric(6, 3))
    M0009808 = db.Column(db.Numeric(6, 3))
    M0009809 = db.Column(db.Numeric(6, 3))
    M0009810 = db.Column(db.Numeric(6, 3))
    M0009811 = db.Column(db.Numeric(6, 3))


# 这里面是区分大小写的：M和m不一样

class lending_rate(db.Model):
    __tablename__ = 'lending_rate'
    datetime = db.Column(db.DateTime, primary_key=True)
    M0009812 = db.Column(db.Numeric(6, 3))
    M0009813 = db.Column(db.Numeric(6, 3))
    M0009814 = db.Column(db.Numeric(6, 3))
    M0009815 = db.Column(db.Numeric(6, 3))
    M0009816 = db.Column(db.Numeric(6, 3))


class deposit_reserve_rate(db.Model):
    __tablename__ = 'deposit_reserve_rate'
    datetime = db.Column(db.DateTime, primary_key=True)
    M0048187 = db.Column(db.Numeric(6, 3))


# 新数据库

class company_list(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'company_list'
    Code = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(80))
    IPO_Date = db.Column(db.DateTime)
    Up_Date = db.Column(db.DateTime)


class cns_stock_basics(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_stock_basics'
    trade_code = db.Column(db.String(20), primary_key=True)
    sec_name = db.Column(db.String(20))
    ipo_date = db.Column(db.DateTime())
    exch_city = db.Column(db.String(20))
    industry_gics = db.Column(db.String(20))
    concept = db.Column(db.String(200))
    curr = db.Column(db.String(20))
    fiscaldate = db.Column(db.String(20))
    auditor = db.Column(db.String(200))
    province = db.Column(db.String(20))
    city = db.Column(db.String(20))
    founddate = db.Column(db.DateTime())
    nature1 = db.Column(db.String(20))
    boardchairmen = db.Column(db.String(20))
    holder_controller = db.Column(db.String(20))
    website = db.Column(db.String(10000))
    phone = db.Column(db.String(200))
    majorproducttype = db.Column(db.String(200))
    majorproductname = db.Column(db.String(2000))


class cns_balance_sheet(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_balance_sheet'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20))
    sec_name = db.Column(db.String(80))
    the_data = db.Column(db.String(80))
    monetary_cap = db.Column(db.Numeric(20, 3))
    tradable_fin_assets = db.Column(db.Numeric(20, 3))
    notes_rcv = db.Column(db.Numeric(20, 3))
    acct_rcv = db.Column(db.Numeric(20, 3))
    prepay = db.Column(db.Numeric(20, 3))
    int_rcv = db.Column(db.Numeric(20, 3))
    dvd_rcv = db.Column(db.Numeric(20, 3))
    inventories = db.Column(db.Numeric(20, 3))
    non_cur_assets_due_within_1y = db.Column(db.Numeric(20, 3))
    oth_cur_assets = db.Column(db.Numeric(20, 3))
    fin_assets_avail_for_sale = db.Column(db.Numeric(20, 3))
    held_to_mty_invest = db.Column(db.Numeric(20, 3))
    long_term_rec = db.Column(db.Numeric(20, 3))
    long_term_eqy_invest = db.Column(db.Numeric(20, 3))
    invest_real_estate = db.Column(db.Numeric(20, 3))
    fix_assets = db.Column(db.Numeric(20, 3))
    const_in_prog = db.Column(db.Numeric(20, 3))
    proj_matl = db.Column(db.Numeric(20, 3))
    fix_assets_disp = db.Column(db.Numeric(20, 3))
    productive_bio_assets = db.Column(db.Numeric(20, 3))
    oil_and_natural_gas_assets = db.Column(db.Numeric(20, 3))
    intang_assets = db.Column(db.Numeric(20, 3))
    r_and_d_costs = db.Column(db.Numeric(20, 3))
    goodwill = db.Column(db.Numeric(20, 3))
    long_term_deferred_exp = db.Column(db.Numeric(20, 3))
    deferred_tax_assets = db.Column(db.Numeric(20, 3))
    oth_non_cur_assets = db.Column(db.Numeric(20, 3))
    st_borrow = db.Column(db.Numeric(20, 3))
    tradable_fin_liab = db.Column(db.Numeric(20, 3))
    notes_payable = db.Column(db.Numeric(20, 3))
    acct_payable = db.Column(db.Numeric(20, 3))
    adv_from_cust = db.Column(db.Numeric(20, 3))
    empl_ben_payable = db.Column(db.Numeric(20, 3))
    taxes_surcharges_payable = db.Column(db.Numeric(20, 3))
    int_payable = db.Column(db.Numeric(20, 3))
    dvd_payable = db.Column(db.Numeric(20, 3))
    oth_payable = db.Column(db.Numeric(20, 3))
    non_cur_liab_due_within_1y = db.Column(db.Numeric(20, 3))
    oth_cur_liab = db.Column(db.Numeric(20, 3))
    lt_borrow = db.Column(db.Numeric(20, 3))
    bonds_payable = db.Column(db.Numeric(20, 3))
    lt_payable = db.Column(db.Numeric(20, 3))
    specific_item_payable = db.Column(db.Numeric(20, 3))
    provisions = db.Column(db.Numeric(20, 3))
    deferred_tax_liab = db.Column(db.Numeric(20, 3))
    oth_non_cur_liab = db.Column(db.Numeric(20, 3))
    cap_stk = db.Column(db.Numeric(20, 3))
    cap_rsrv = db.Column(db.Numeric(20, 3))
    tsy_stk = db.Column(db.Numeric(20, 3))
    surplus_rsrv = db.Column(db.Numeric(20, 3))
    undistributed_profit = db.Column(db.Numeric(20, 3))

class cns_income_statement(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_income_statement'
    stock_code = db.Column(db.String(10), db.ForeignKey('cns_stock_basics.trade_code'), primary_key=True)
    sec_name = db.Column(db.String(40))
    the_date = db.Column(db.String(40), primary_key=True)
    oper_rev = db.Column(db.Numeric(20, 3))
    oper_cost = db.Column(db.Numeric(20, 3))
    taxes_surcharges_ops = db.Column(db.Numeric(20, 3))
    selling_dist_exp = db.Column(db.Numeric(20, 3))
    gerl_admin_exp = db.Column(db.Numeric(20, 3))
    fin_exp_is = db.Column(db.Numeric(20, 3))
    impair_loss_assets = db.Column(db.Numeric(20, 3))
    net_gain_chg_fv = db.Column(db.Numeric(20, 3))
    net_invest_inc = db.Column(db.Numeric(20, 3))
    opprofit = db.Column(db.Numeric(20, 3))
    non_oper_rev = db.Column(db.Numeric(20, 3))
    non_oper_exp= db.Column(db.Numeric(20, 3))
    tax = db.Column(db.Numeric(20, 3))
    tot_profit = db.Column(db.Numeric(20, 3))
    net_profit_is = db.Column(db.Numeric(20, 3))
    eps_basic_is= db.Column(db.Numeric(20, 3))
    eps_diluted_is=db.Column(db.Numeric(20, 3))

class cns_statement_of_cash_flows(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_statement_of_cash_flows'
    stock_code = db.Column(db.String(10), db.ForeignKey('cns_stock_basics.trade_code'), primary_key=True)
    sec_name = db.Column(db.String(40))
    the_date = db.Column(db.String(40), primary_key=True)
    cash_recp_sg_and_rs = db.Column(db.Numeric(20, 3))
    recp_atx_rends = db.Column(db.Numeric(20, 3))
    other_cash_recp_ral_oper_act = db.Column(db.Numeric(20, 3))
    stot_cash_inflows_oper_act = db.Column(db.Numeric(20, 3))
    csah_pay_goods_purch_serv_rec = db.Column(db.Numeric(20, 3))
    cash_pay_beh_empl = db.Column(db.Numeric(20, 3))
    pay_all_typ_tax = db.Column(db.Numeric(20, 3))
    other_cash_pay_ral_oper_act = db.Column(db.Numeric(20, 3))
    stot_cash_outflows_oper_act = db.Column(db.Numeric(20, 3))
    net_cash_flows_oper_act = db.Column(db.Numeric(20, 3))
    cash_recp_disp_withdrwl_invest = db.Column(db.Numeric(20, 3))
    cash_recp_return_invest= db.Column(db.Numeric(20, 3))
    net_cash_recp_disp_fiolta = db.Column(db.Numeric(20, 3))
    other_cash_recp_ral_inv_act = db.Column(db.Numeric(20, 3))
    stot_cash_inflows_inv_act = db.Column(db.Numeric(20, 3))
    cash_pay_acq_const_fiolta = db.Column(db.Numeric(20, 3))
    cash_paid_invest = db.Column(db.Numeric(20, 3))
    other_cash_pay_ral_inv_act= db.Column(db.Numeric(20, 3))
    stot_cash_outflow_inv_act= db.Column(db.Numeric(20, 3))
    net_cash_flows_inv_act = db.Column(db.Numeric(20, 3))
    cash_recp_cap_contrib = db.Column(db.Numeric(20, 3))
    cash_recp_borrow= db.Column(db.Numeric(20, 3))
    other_cash_recp_ral_fnc_act= db.Column(db.Numeric(20, 3))
    stot_cash_inflows_fnc_act = db.Column(db.Numeric(20, 3))
    cash_prepay_amt_borr = db.Column(db.Numeric(20, 3))
    cash_pay_dist_dpcp_int_exp = db.Column(db.Numeric(20, 3))
    other_cash_pay_ral_fnc_act = db.Column(db.Numeric(20, 3))
    stot_cash_outflows_fnc_act= db.Column(db.Numeric(20, 3))
    net_cash_flows_fnc_act= db.Column(db.Numeric(20, 3))
    eff_fx_flu_cash = db.Column(db.Numeric(20, 3))
    net_incr_cash_cash_equ_dm = db.Column(db.Numeric(20, 3))
    cash_cash_equ_beg_period= db.Column(db.Numeric(20, 3))
    cash_cash_equ_end_period= db.Column(db.Numeric(20, 3))
    net_profit_cs = db.Column(db.Numeric(20, 3))
    prov_depr_assets = db.Column(db.Numeric(20, 3))
    depr_fa_coga_dpba= db.Column(db.Numeric(20, 3))
    amort_intang_assets= db.Column(db.Numeric(20, 3))
    amort_lt_deferred_exp = db.Column(db.Numeric(20, 3))
    loss_disp_fiolta = db.Column(db.Numeric(20, 3))
    loss_scr_fa = db.Column(db.Numeric(20, 3))
    loss_fv_chg= db.Column(db.Numeric(20, 3))
    fin_exp_cs= db.Column(db.Numeric(20, 3))
    invest_loss = db.Column(db.Numeric(20, 3))
    decr_deferred_inc_tax_assets = db.Column(db.Numeric(20, 3))
    incr_dererred_inc_tax_liab= db.Column(db.Numeric(20, 3))
    decr_inventories= db.Column(db.Numeric(20, 3))
    decr_oper_payable = db.Column(db.Numeric(20, 3))
    incr_oper_payable = db.Column(db.Numeric(20, 3))
    others= db.Column(db.Numeric(20, 3))
    im_net_cash_flows_oper_act= db.Column(db.Numeric(20, 3))
    conv_corp_bonds_due_within_1y = db.Column(db.Numeric(20, 3))
    fa_fnc_leases = db.Column(db.Numeric(20, 3))
    end_bal_cash= db.Column(db.Numeric(20, 3))
    beg_bal_cash= db.Column(db.Numeric(20, 3))
    end_bal_cash_equ = db.Column(db.Numeric(20, 3))
    beg_bal_cash_equ = db.Column(db.Numeric(20, 3))
    net_incr_cash_cash_equ_im= db.Column(db.Numeric(20, 3))

class cns_financial_target_1(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_financial_target_1'
    id_1 = db.Column(db.String(10), primary_key=True)
    cn_name_1 = db.Column(db.String(40))
    en_name_1 = db.Column(db.String(40))

class cns_financial_target_2(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_financial_target_2'
    id_2 = db.Column(db.String(10), primary_key=True)
    cn_name_2 = db.Column(db.String(40))
    en_name_2 = db.Column(db.String(40))
    id_belong_to_1=db.Column(db.String(10), db.ForeignKey('cns_financial_target_1.id_1'))

class cns_financial_target_3(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_financial_target_3'
    id_3 = db.Column(db.String(10), primary_key=True)
    cn_name_3 = db.Column(db.String(40))
    en_name_3 = db.Column(db.String(40))
    id_belong_to_2=db.Column(db.String(10), db.ForeignKey('cns_financial_target_2.id_2'))

class cns_financial_target_4(db.Model):
    __bind_key__ = 'cns_stock'
    __tablename__ = 'cns_financial_target_4'
    id_4 = db.Column(db.String(10), primary_key=True)
    cn_name_4 = db.Column(db.String(40))
    en_name_4 = db.Column(db.String(40))
    id_belong_to_3=db.Column(db.String(10), db.ForeignKey('cns_financial_target_3.id_3'))
