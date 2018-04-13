# # coding: UTF-8
#
# # 初始化接口#
# from WindPy import *
# import pandas as pd
# import json
# from webapp.models import *
# import MySQLdb, time, re
# import time as Time
# from sqlalchemy import create_engine, or_, func, desc, distinct  # me func用于计数,desc用于逆序找max值
# from sqlalchemy.orm import sessionmaker
# import numpy as np
# import xlrd,os
#
# # 测试期间所有函数只读取两条股票
#
# def upData_company_list():
#     data ={}
#     db_engine = create_engine('mysql://root:0000@localhost/test?charset=utf8')
#     Session = sessionmaker(bind=db_engine)
#     session = Session()
#     data = xlrd.open_workbook(os.path.abspath(os.path.dirname(__file__))+'/new.xlsx')
#     # 获取分数表
#     table = data.sheet_by_name(u'sheet_score')
#     list_stock_code = np.array(table.col_values(0))
#     list_score = np.array(table.col_values(8))
#     print list_score
#     list_score.astype('float64')
#     # 取大于得分20%，40%，60%，80%分位数
#     quantile_20 =np.percentile(list_score,20)
#     quantile_40 = np.percentile(list_score,40)
#     quantile_60 = np.percentile(list_score,60)
#     quantile_80 = np.percentile(list_score,80)
#     print quantile_80
#     for i in range(0,len(list_stock_code)):
#         result = stock_grade_l.query.filter_by(trade_code=list_stock_code[i]).first()
#         if result is None:
#             continue
#         else:
#             position = np.where(list_stock_code == result.trade_code)
#             print list_score[position]
#             if list_score[position] >= quantile_80:
#                 result.grade_id='1'
#                 db.session.commit()
#                 print result.trade_code
#             elif list_score[position] >= quantile_60:
#                 result.grade_id='4'
#                 db.session.commit()
#                 print result.trade_code
#             elif list_score[position] >= quantile_40:
#                 result.grade_id='7'
#                 db.session.commit()
#                 print result.trade_code
#             elif list_score[position] >= quantile_20:
#                 result.grade_id='10'
#                 db.session.commit()
#                 print result.trade_code
#             else:
#                 result.grade_id='11'
#                 db.session.commit()
#                 print result.trade_code
#
#     return data
#
#
# def upData_cns_stock_basics():
#     db_engine = create_engine('mysql://root:0000@localhost/cns_stock_basics?charset=utf8')
#     Session = sessionmaker(bind=db_engine)
#     session = Session()
#     w.start();
#     # 获取所有A股代码#
#     AllAStock = w.wset("SectorConstituent", "date=20180304;sectorId=a001010100000000;field=wind_code");
#     if AllAStock.ErrorCode != 0:
#         print("Get Data failed! exit!")
#         exit()
#     # for stock in AllAStock.Data[0]:
#     for i in range(0, 2):
#         stock = AllAStock.Data[0][i]
#         wdata = w.wsd(stock,
#                       "sec_name,ipo_date,exch_city,industry_gics,concept,curr,fiscaldate,auditor,province,city,founddate,nature1,boardchairmen,holder_controller,website,phone,majorproducttype,majorproductname",
#                       "2018-02-03", "2018-03-04", "industryType=1;Period=Y;Days=Weekdays")
#         print(wdata)
#         # 更新cns_stock_basics
#         updata = cns_stock_basics()
#         updata.trade_code = stock[0:6]
#         updata.sec_name = wdata.Data[0]
#         updata.ipo_date = wdata.Data[1]
#         updata.exch_city = wdata.Data[2]
#         updata.industry_gics = wdata.Data[3]
#         updata.concept = wdata.Data[4]
#         updata.curr = wdata.Data[5]
#         updata.fiscaldate = wdata.Data[6]
#         updata.auditor = wdata.Data[7]
#         updata.province = wdata.Data[8]
#         updata.city = wdata.Data[9]
#         updata.founddate = wdata.Data[10]
#         updata.nature1 = wdata.Data[11]
#         updata.boardchairmen = wdata.Data[12]
#         updata.holder_controller = wdata.Data[13]
#         updata.website = wdata.Data[14]
#         updata.phone = wdata.Data[15]
#         updata.majorproducttype = wdata.Data[16]
#         updata.majorproductname = wdata.Data[17]
#         db.session.add(updata)
#     db.session.commit()
#
#
# def upData_cns_balance_sheet():
#     db_engine = create_engine('mysql://root:0000@localhost/upData_cns_balance_sheet?charset=utf8')
#     Session = sessionmaker(bind=db_engine)
#     session = Session()
#     w.start();
#     # 获取所有A股代码#
#     AllAStock = w.wset("SectorConstituent", "date=20180304;sectorId=a001010100000000;field=wind_code");
#     if AllAStock.ErrorCode != 0:
#         print("Get Data failed! exit!")
#         exit()
#     # for stock in AllAStock.Data[0]:
#     for i in range(0, 2):
#         stock = AllAStock.Data[0][i]
#         wdata = w.wsd(stock,
#                       "sec_name,monetary_cap,tradable_fin_assets,notes_rcv,acct_rcv,prepay,int_rcv,dvd_rcv,inventories,non_cur_assets_due_within_1y,oth_cur_assets,fin_assets_avail_for_sale,held_to_mty_invest,long_term_rec,long_term_eqy_invest,invest_real_estate,fix_assets,const_in_prog,proj_matl,fix_assets_disp,productive_bio_assets,oil_and_natural_gas_assets,intang_assets,r_and_d_costs,goodwill,long_term_deferred_exp,deferred_tax_assets,oth_non_cur_assets,st_borrow,tradable_fin_liab,notes_payable,acct_payable,adv_from_cust,empl_ben_payable,taxes_surcharges_payable,int_payable,dvd_payable,oth_payable,non_cur_liab_due_within_1y,oth_cur_liab,lt_borrow,bonds_payable,lt_payable,specific_item_payable,provisions,deferred_tax_liab,oth_non_cur_liab,cap_stk,cap_rsrv,tsy_stk,surplus_rsrv,undistributed_profit",
#                       "ED-1Y", "2018-03-05", "unit=1;rptType=1;Period=Q;Days=Weekdays")
#         print(wdata.Data)
#         # print(wdata.Data[1])
#         # print(wdata.Data[2])
#         # 更新cns_stock_basics
#         for i in range(0, len(wdata.Times)):
#             updata = cns_balance_sheet()
#             updata.stock_code = stock[0:6]
#             updata.the_data = wdata.Times[i]
#             updata.sec_name = wdata.Data[0][i]
#             updata.monetary_cap = wdata.Data[1][i]
#             updata.tradable_fin_assets = wdata.Data[2][i]
#             updata.notes_rcv = wdata.Data[3][i]
#             updata.acct_rcv = wdata.Data[4][i]
#             updata.prepay = wdata.Data[5][i]
#             updata.int_rcv = wdata.Data[6][i]
#             updata.dvd_rcv = wdata.Data[7][i]
#             updata.inventories = wdata.Data[8][i]
#             updata.non_cur_assets_due_within_1y=wdata.Data[9][i]
#             updata.oth_cur_assets = wdata.Data[10][i]
#             updata.fin_assets_avail_for_sale = wdata.Data[11][i]
#             updata.held_to_mty_invest = wdata.Data[12][i]
#             updata.long_term_rec = wdata.Data[13][i]
#             updata.long_term_eqy_invest = wdata.Data[14][i]
#             updata.invest_real_estate = wdata.Data[15][i]
#             updata.fix_assets = wdata.Data[16][i]
#             updata.const_in_prog = wdata.Data[17][i]
#             updata.proj_matl = wdata.Data[18][i]
#             updata.fix_assets_disp = wdata.Data[19][i]
#             updata.productive_bio_assets = wdata.Data[20][i]
#             updata.oil_and_natural_gas_assets = wdata.Data[21][i]
#             updata.intang_assets = wdata.Data[22][i]
#             updata.r_and_d_costs = wdata.Data[23][i]
#             updata.goodwill = wdata.Data[24][i]
#             updata.long_term_deferred_exp = wdata.Data[25][i]
#             updata.deferred_tax_assets = wdata.Data[26][i]
#             updata.oth_non_cur_assets = wdata.Data[27][i]
#             updata.st_borrow = wdata.Data[28][i]
#             updata.tradable_fin_liab = wdata.Data[29][i]
#             updata.notes_payable = wdata.Data[30][i]
#             updata.acct_payable = wdata.Data[31][i]
#             updata.adv_from_cust = wdata.Data[32][i]
#             updata.empl_ben_payable = wdata.Data[33][i]
#             updata.taxes_surcharges_payable = wdata.Data[34][i]
#             updata.int_payable = wdata.Data[35][i]
#             updata.dvd_payable = wdata.Data[36][i]
#             updata.oth_payable = wdata.Data[37][i]
#             updata.non_cur_liab_due_within_1y = wdata.Data[38][i]
#             updata.oth_cur_liab = wdata.Data[39][i]
#             updata.lt_borrow = wdata.Data[40][i]
#             updata.bonds_payable = wdata.Data[41][i]
#             updata.lt_payable = wdata.Data[42][i]
#             updata.specific_item_payable = wdata.Data[43][i]
#             updata.provisions = wdata.Data[44][i]
#             updata.deferred_tax_liab = wdata.Data[45][i]
#             updata.oth_non_cur_liab = wdata.Data[46][i]
#             updata.cap_stk = wdata.Data[47][i]
#             updata.cap_rsrv = wdata.Data[48][i]
#             updata.tsy_stk = wdata.Data[49][i]
#             updata.surplus_rsrv = wdata.Data[50][i]
#             updata.undistributed_profit = wdata.Data[51][i]
#             db.session.add(updata)
#     db.session.commit()
#     return wdata.Data
#
