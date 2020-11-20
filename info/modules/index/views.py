# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 23:30
# @ Software:PyCharm
from . import index_blue
from info import redis_store
import logging
from flask import current_app, render_template, session

from ...models import User


@index_blue.route('/', methods=['POST', 'GET'])
def hello():

    # 测试redis存取数据
    # redis_store.set('name', '老王')
    # print(redis_store.get('name'))

    # 测试session存取
    # session['name'] = '张三'
    # print(session.get('name'))

    # 没有继承日志之前，使用print输出,不方便做控制
    # print('hello_world')

    # 使用日志记录方法logging进行输出可控
    # logging.debug('输出调试信息')
    # logging.info('输出详细信息')
    # logging.warning('输出警告信息')
    # logging.error('输出错误信息')

    # 也可以使用current_app来输出日志信息
    # current_app.logger.debug('输出调试信息2')
    # current_app.logger.info('输出详细信息2')
    # current_app.logger.warning('输出警告信息2')
    # current_app.logger.error('输出错误信息2')


    # 1.获取用户的登录信息
    user_id = session.get('user_id')

    # 2.通过user_id取出用户对象
    user = None
    if user_id:
        try:
            user = User.query.filter(User.id == user_id).first()
        except Exception as e:
            current_app.logger(e)
    # 3.拼接用户数据，渲染页面

    data = {
        "user_info": user.to_dict() if user else "",
    }

    return render_template('news/index.html', data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')