# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 22:59
# @ Software:PyCharm
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf import CSRFProtect
from config import config_dict

# 定义redis_store变量
redis_store = None
# 定义db变量
db = SQLAlchemy()


# 定义工厂方法
def create_app(config_name):

    app = Flask(__name__)

    # 根据传入的配置类名称，去除对应的配置类
    config = config_dict.get(config_name)

    # 调用日志方法，记录程序运行信息
    log_file(config.LEVEL_NAME)

    # 加载配置类
    app.config.from_object(config)

    # 创建SQLAlchemy对象，关联app
    db.init_app(app)

    # 创建redis对象
    global redis_store  # 将局部变量声明为一个全局的
    redis_store = StrictRedis(host=config.REDIS_HOST,
                              port=config.REDIS_PORT,
                              decode_responses=True)

    # 创建Session对象，读取app中的session配置
    Session(app)

    # 使用CSRFProtect保护app
    CSRFProtect(app)

    from info.modules.index import index_blue
    # 将index_blue蓝图注册到app
    app.register_blueprint(index_blue)

    return app


def log_file(LEVEL_NAME):
    # 设置日志的记录等级,常见的有四种，大小关系如下：DEBUG<INFO<WARNING<ERROR
    logging.basicConfig(level=LEVEL_NAME)  # 调试DEBUG级, 一旦设置级别，那么大于等于该级别的信息全部都会输出
    # 创建日志记录器，指明日志保存的路径，每个日志文件最大大小，保存的日志文件个数上限
    file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式，日志等级，输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)