# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 20:58
# @ Software:PyCharm
"""
相关配置信息
1.数据库配置
2.redis配置
    缓存访问频率高的内容，存储session信息，图片验证码，短信验证码
3.session配置
    将来用来保存用户的登录信息
4.csrf配置
    保护app防止csrf攻击
    校验的请求方式：'POST', 'PUT', 'PATCH', 'DELETE'
"""
from datetime import timedelta

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf import CSRFProtect

app = Flask(__name__)


# 设置配置信息
class Config(object):
    # 调式信息
    DEBUG = True

    SECRET_KEY = 'hard to guess!'

    # 配置数据库信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:li990407@localhost:3306/project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # session配置信息
    SESSION_TYPE = 'redis'  # 设置session存储类型
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                                decode_responses=True)  # 指定session存储的redis服务器
    SESSION_USE_SIGNER = True  # 设置session签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)  # 设置session的有效期2天


app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)

# 创建redis对象
redis_store = StrictRedis(host=app.config.get('REDIS_HOST'),
                          port=app.config.get('REDIS_PORT'),
                          decode_responses=True)

# 创建Session对象，读取app中的session配置
Session(app)

# 使用CSRFProtect保护app
CSRFProtect(app)


@app.route('/', methods=["POST", "GET"])
def hello():

    # 测试redis存取数据
    redis_store.set('name', '老王')
    print(redis_store.get('name'))

    # 测试session存取
    session['name'] = '张三'
    print(session.get('name'))

    return "hello"


if __name__ == "__main__":
    app.run()