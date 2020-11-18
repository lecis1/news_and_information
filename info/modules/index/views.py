# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 23:30
# @ Software:PyCharm
from . import index_blue
from info import redis_store
import logging
from flask import current_app


@index_blue.route('/', methods=['POST', 'GET'])
def hello():

    # 测试redis存取数据
    # redis_store.set('name', '老王')
    # print(redis_store.get('name'))

    # 测试session存取
    # session['name'] = '张三'
    # print(session.get('name'))

    # 没有继承日志之前，使用print输出,不方便做控制
    print('hello_world')

    # 使用日志记录方法logging进行输出可控
    logging.debug('输出调试信息')
    logging.info('输出详细信息')
    logging.warning('输出警告信息')
    logging.error('输出错误信息')

    # 也可以使用current_app来输出日志信息
    # current_app.logger.debug('输出调试信息2')
    # current_app.logger.info('输出详细信息2')
    # current_app.logger.warning('输出警告信息2')
    # current_app.logger.error('输出错误信息2')

    return "hello_world"
