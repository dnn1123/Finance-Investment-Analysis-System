# encoding:utf-8
# 程序配置文件
import os
class Config(object):
    pass


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0000@localhost:3306/test'
    SQLALCHEMY_BINDS = {
    'users_info':        'mysql+pymysql://root:0000@localhost:3306/users_info',
        'quant':          'mysql+pymysql://root:0000@localhost:3306/quant',
        'my_message': 'mysql+pymysql://root:0000@localhost:3306/my_message',
        'cns_stock': 'mysql+pymysql://root:0000@localhost:3306/cns_stock',
    }
    SECRET_KEY = 'you-will-never-guess'
    JOBS = [
        {
            'id': 'job1',
            'func': 'clientapp:send_notice',
            'args': '',
            # 'trigger': {
            #     'type': 'cron',
            #     'day_of_week': "mon-fri",
            #     'hour': '0-23',
            #     'minute': '0-11',
            #     'second': '*/5'
            # }
            'trigger': 'interval',
            'seconds': 30

        }
    ]
    SCHEDULER_API_ENABLED = True


class paths(object):
    project_path=os.path.dirname(os.path.realpath(__file__))
    root_path=os.path.dirname(project_path)