#encoding:utf-8
#程序配置文件
class Config(object):
    pass


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:0000@localhost:3306/test'
    SECRET_KEY = 'you-will-never-guess'
