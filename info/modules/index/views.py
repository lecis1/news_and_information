# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 23:30
# @ Software:PyCharm
from . import index_blue
from info import redis_store
import logging
from flask import current_app, render_template, session, jsonify, request, g

from ...models import User, News, Category
from ...utils.comments import user_login_data
from ...utils.response_code import RET


@index_blue.route('/', methods=['POST', 'GET'])
@user_login_data
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
            current_app.logger.error(e)

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
        "user_info": g.user.to_dict() if g.user else "",
        "news": new_list,
        "category_list": category_list,
    }

    return render_template('news/index.html', data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
@user_login_data
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')


@index_blue.route('/newslist', methods=["GET"])
def newslist():
    # 1.获取参数
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')

    # 2.参数类型转化
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10

    # 3.分页查询
    try:
        # 判断新闻的分类是否为1
        """
        if cid == "1":
            paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
        else:
            paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page, False)
        """

        """
        # 改装，判断新闻的分类是否为1
        filters = ""
        if cid != "1":
            filters = (News.category_id == cid)
        paginate = News.query.filter(filters).order_by(
            News.create_time.desc()).paginate(page, per_page, False)
        """

        # 再改装，判断新闻的分类是否为1
        filters = []
        if cid != "1":
            filters.append(News.category_id == cid)
        paginate = News.query.filter(*filters).order_by(
            News.create_time.desc()).paginate(page, per_page, False)

    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 4.获取分页对象中的属性，总页数，当前页，当前页的对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表转成字典列表
    news_list = []
    for new in items:
        news_list.append(new.to_dict())

    # 6.携带数据，返回响应
    return jsonify(errno=RET.OK, errmsg="获取新闻成功", totalPage=totalPage, newsList=news_list)