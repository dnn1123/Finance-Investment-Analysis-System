#encoding:utf-8
from webapp.Controller.quant.bpm import sql_to_dict,Strategy,Strategy_Manager
import MySQLdb,datetime
def get_work():
    worklist=[]
    db = MySQLdb.connect("localhost", "root", "0000", "quant",charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 查询语句
    sql = "Select * from subscriber Where status='运行中'"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            params=sql_to_dict(row[4])
            worklist.append({"id":row[2],"params":params,"build_date":row[6],"receiver":row[1]}) #id中可以包含多个值字典 手机号
        return worklist
    except:
        print "Error: unable to fecth data"

    # 关闭数据库连接
    db.close()
def send_notice():
    work_list=get_work()
    for i in work_list:
        if i['id']==Strategy.Pair_Strategy_Based_Bank.value:
            strategy=Strategy_Manager(Strategy.Pair_Strategy_Based_Bank,live=True,cash=i['params']['cash'],commission=i['params']['commission'],builddate=i['build_date'],instrument_1=i['params']['instrument_1'],instrument_2=i['params']['instrument_2'])
            strategy.run()
            message=strategy.getMessage()
            today_message=message.get(datetime.datetime.now().date())
            if today_message:
                letter_send(i['receiver'],today_message)

        if i['id']==Strategy.DoubleMA_Strategy.value:
            strategy=Strategy_Manager(Strategy.DoubleMA_Strategy,live=True,cash=i['params']['cash'],commission=i['params']['commission'],builddate=i['build_date'],instrument=i['params']['instrument'])
            strategy.run()
            message=strategy.getMessage()
            today_message = message.get(datetime.datetime.now().date())
            if today_message:
                letter_send(i['receiver'], today_message)


        if i['id']==Strategy.Buy_Everyday.value:
            strategy=Strategy_Manager(Strategy.Buy_Everyday,live=True,cash=i['params']['cash'],commission=i['params']['commission'],builddate=i['build_date'],instrument=i['params']['instrument'])
            strategy.run()
            message=strategy.getMessage()
            today_message = message.get(datetime.datetime.now().date())
            if today_message:
                letter_send(i['receiver'], today_message)

def letter_send(receiver,text):
    db = MySQLdb.connect("localhost", "root", "0000", "my_message",charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    # SQL 插入语句
    sql = "Insert into personal_information(receiver,sender, message_content, time, state) VALUES ('%s', '%s', '%s', now(), '%s' )" % (receiver, 'system', text, 'N', )
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

    # 关闭数据库连接
    db.close()
