# coding=utf-8
# 按照行业来分组

# sql语句
#SELECT SUM(finance_basics.tot_oper_rev),cns_sub_industry.industry_gics_4 from finance_basics,cns_sub_industry,cns_stock_industry where finance_basics.trade_code=cns_stock_industry.trade_code and cns_stock_industry.industry_gicscode_4=cns_sub_industry.industry_gicscode_4 GROUP BY cns_sub_industry.industry_gicscode_4

# rs1 = session.query(finance_basics.tot_oper_rev,func.sum(finance_basics.tot_oper_rev),cns_sub_industry.industry_gicscode_4,cns_sub_industry.industry_gics_4).filter(finance_basics.the_year=='20151231').filter(finance_basics.trade_code==cns_stock_industry.trade_code).filter(cns_stock_industry.industry_gicscode_4==cns_sub_industry.industry_gicscode_4).group_by(cns_sub_industry.industry_gicscode_4).all()
# 结果如下
# (Decimal('428036742.170'), Decimal('4337736275.830'), u'10101010', u'\u77f3\u6cb9\u5929\u7136\u6c14\u94bb\u4e95')

# rs2 = session.query(func.sum(finance_basics.tot_oper_rev),func.sum(finance_basics.net_profit_is),func.sum(finance_basics.wgsd_com_eq),func.sum(finance_basics.tot_assets),func.sum(finance_basics.tot_liab),func.sum(finance_basics.wgsd_com_eq),func.sum(finance_basics.operatecashflow_ttm2),func.sum(finance_basics.investcashflow_ttm2),func.sum(finance_basics.financecashflow_ttm2),func.sum(finance_basics.cashflow_ttm2),cns_sub_industry.industry_gicscode_4,cns_sub_industry.industry_gics_4).filter(finance_basics.trade_code==cns_stock_industry.trade_code).filter(cns_stock_industry.industry_gicscode_4==cns_sub_industry.industry_gicscode_4).filter(cns_sub_industry.industry_gicscode_4=='25102010').group_by(finance_basics.the_year).all()
