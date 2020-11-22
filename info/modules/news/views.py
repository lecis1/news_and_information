# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/21 11:50
# @ Software:PyCharm
from flask import current_app, jsonify, render_template, abort, session, g, \
    request

from . import news_blue


# 请求路径：/news/<int:news_id>
# 请求方式：GET
# 请求参数：news_id
# 返回值：detail.html页面，用户data字典数据
from ... import db
from ...models import News, User, Comment
from ...utils.comments import user_login_data
from ...utils.response_code import RET


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    # # 0.从session中取出用户的user_id
    # user_id = session.get('user_id')
    # # 0.1通过user_id取出用户对象
    # user = None
    #
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    # 1.根据新闻编号查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 如果新闻对像不存在直接抛出异常、
    if not news:
        abort(404)

    # 获取前六条热门新闻
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    # 将热门新闻的对象列表转成字典列表
    click_news_list = []
    for new in click_news:
        click_news_list.append(new.to_dict())

    # 判断用户是否收藏过该新闻
    is_collected = False
    # 用户需要登录，并且该新闻在用户收藏过的新闻列表中
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 查询数据库中该新闻的所有的评论内容
    try:

        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")
    # 将评论的对象列表转成字典列表
    comments_list = []
    for comment in comments:
        comments_list.append(comment.to_dict())

    # .携带数据渲染页面
    data = {
        "news_info": news.to_dict(),
        "user_info": g.user.to_dict() if g.user else "",
        "news": click_news_list,
        "is_collected": is_collected,
        "comments": comments_list
    }
    return render_template('news/detail.html', data=data)


# 收藏接口功能
# 请求路径：/news/news_collect
# 请求方式：POST
# 请求参数： news_id, action, g.user
# 返回值：errno, errmsg
@news_blue.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    # 1.判断用户登录状态
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')

    # 2.获取参数
    news_id = request.json.get('news_id')
    action = request.json.get('action')

    # 3.参数校验，为空校验
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数为空")

    # 4.操作类型
    if not action in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")

    # 5.根据新闻编号取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="新闻获取失败")

    # 6.判断新闻对象是否存
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 7.判断操作类型
    if action == "collect":
        # 7.1判断用户是否未收藏过该新闻
        if not news in g.user.collection_news:
            g.user.collection_news.append(news)
    else:
        # 7.2判断用户是否收藏过该新闻
        if news in g.user.collection_news:
            g.user.collection_news.remove(news)

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


# 新闻评论后端
# 请求路径：POST
# 请求参数：news_id， comment， parent_id, g.user
# 返回值：errno, errmsg, 评论字典
@news_blue.route('/news_comment', methods=['POST'])
@user_login_data
def news_comment():
    # 1.判断用户是否登录
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    # 2.获取请求参数

    news_id = request.json.get('news_id')
    content = request.json.get('comment')
    parent_id = request.json.get('parent_id')

    # 3.校验参数，为空校验
    if not all([news_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4.根据新闻编号取出新闻对象，判断新闻是否存在
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    if not news: return jsonify(errno=RET.NODATA, errmsg="新闻不存在")

    # 5.创建评论对象，设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id

    # 6.保存评论对象到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论失败")

    # 7.返回响应，携带评论数据

    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())

