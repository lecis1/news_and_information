# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/21 11:50
# @ Software:PyCharm
from . import news_blue


@news_blue.route('/news_detail')
def news_detail():
    return "展示新闻详情"