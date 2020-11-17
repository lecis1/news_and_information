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
4.csrf配置
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

app = Flask(__name__)


# 设置配置信息
class Config(object):
    # 调式信息
    DEBUG = True

    # 配置数据库信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:li990407@localhost:3306/project'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #redis配置信息
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)

# 创建redis对象
redis_store = StrictRedis(host=app.config.get('REDIS_HOST'),
                          port=app.config.get('REDIS_PORT'),
                          decode_responses=True)


@app.route('/')
def hello():

    # 测试redis存取数据
    redis_store.set('name', '老王')

    print(redis_store.get('name'))

    return "hello"


if __name__ == "__main__":
    app.run()