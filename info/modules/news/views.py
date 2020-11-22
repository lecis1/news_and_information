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
from ...models import News, User, Comment, CommentLike
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

    # 获取用户点过赞的评论编号
    # .1获取用户点过的所有的赞
    try:
        comment_likes = []
        if g.user:
            comment_likes = CommentLike.query.filter(CommentLike.user_id == g.user.id).all()
        #  .2获取用户点赞的所有评论的编号
        mylike_comment_ids = []
        for comment_like in comment_likes:
            mylike_comment_ids.append(comment_like.comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取点赞失败")

    # 将评论的对象列表转成字典列表
    comments_list = []
    for comment in comments:
        # 将评论对象转字典
        comm_dict = comment.to_dict()

        # 判断用户是否有对评论点过赞
        if g.user and comment.id in mylike_comment_ids:
            # 添加key-value记录点赞
            comm_dict['is_like'] = False

        comments_list.append(comm_dict)

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


# 评论点赞
# 请求路径：/news/comment_like
# 请求方式post
# 请求参数:1.评论编号news_id
#         2.用户需要登录g.user
#         3.操作类型action
# 返回值：errno,errmsg
@app.route('/comment_like', methods=['POST'])
def comment_like():
    # 1判断用户是否登录
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    # 2获取参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    # 3参数校验，为空校验
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4操作类型进行校验
    if not action in(["add", "remove"]):
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")

    # 5通过评论编号查询评论对象是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 6根据操作类型点赞或取消点赞
    try:
        if action == "add":
            # 判断用户是否对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id, CommentLike.comment_id == comment_id).first()
            if not comment_like:
                # 创建点赞对象
                comment_like = CommentLike()
                comment_like.user_id = g.user.id
                comment_like.comment_id = comment_id

                # 添加到数据库
                db.session.add(comment_like)

                # 将该评论的点赞数量+1
                comment.like_count += 1

                db.session.commit()

        else:
            # 判断用户是否对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id, CommentLike.comment_id == comment_id).first()
            if comment_like:
                # 删除点赞对象
                db.session.delete(comment_like)

                # 将该评论的点赞数量-1
                if comment.like_count > 0:
                    comment.like_count -= 1

                db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作失败")
    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")

