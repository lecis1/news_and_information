# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 23:30
# @ Software:PyCharm
from . import index_blue
from info import redis_store


@index_blue.route('/', methods=['POST', 'GET'])
def hello():

    # 测试redis存取数据
    redis_store.set('name', '老王')
    print(redis_store.get('name'))

    # 测试session存取
    # session['name'] = '张三'
    # print(session.get('name'))

    return "hello_world"
