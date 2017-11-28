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


class roles1(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'users_role'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), db.ForeignKey('users.username'))
    permissions = db.Column(db.Integer)


# 权限常量
class Permission:
    administrator = 1
    trader = 2
    visitor = 3


class users(UserMixin, db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'users'
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(45))

    # def __init__(self, **kwargs):
    #     super(User, self).__init__(**kwargs)
    def can(self, permissions):
        result = roles1.query.filter_by(user_name=self.username).first()
        return result is not None and \
               result.permissions <= permissions

    def is_administrator(self):
        return self.can(Permission.administrator)

    roles = db.relationship(
            'Role',
            secondary=roles,
            backref=db.backref('users', lazy='dynamic')
    )

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


class Role(db.Model):
    __bind_key__ = 'users_info'
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


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



