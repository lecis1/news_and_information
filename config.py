# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 22:43
# @ Software:PyCharm
from redis import StrictRedis
from datetime import timedelta


class Config(object):
    """设置基类配置信息"""
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


class DevelopConfig(Config):
    """开发环境配置信息"""
    SQLALCHEMY_DATABASE_URI = 'mysql://root:li990407@localhost:3306/development'


class ProductConfig(Config):
    """生产环境配置信息（线上）"""
    DEBUG = False


class TestConfig(Config):
    """测试环境配置信息"""
    pass


# 提供统一的访问入口

config_dict = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "test": TestConfig,
}