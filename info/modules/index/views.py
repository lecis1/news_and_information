# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 23:30
# @ Software:PyCharm
from . import index_blue
from info import redis_store
import logging
from flask import current_app, render_template, session, jsonify

from ...models import User, News, Category
from ...utils.response_code import RET


@index_blue.route('/', methods=['POST', 'GET'])
def show_index():

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

    # 3 查询热门新闻，根据点击量查询前十条新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 4将新闻的对象列表转为字典列表
    new_list = []
    for new in news:
        new_list.append(new.to_dict())

    # 5查询所有的分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg=" 获取分类失败")

    # 6将分类的数据列表转成字典列表
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 3.拼接用户数据，渲染页面

    data = {
        "user_info": user.to_dict() if user else "",
        "news": new_list,
        "category_list": category_list,
    }

    return render_template('news/index.html', data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')