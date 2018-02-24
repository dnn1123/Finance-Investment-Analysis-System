# encoding:utf-8
# 程序配置文件
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
    }
    SECRET_KEY = 'you-will-never-guess'