# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/21 9:14
# @ Software:PyCharm
# 自定义过滤器实现热门新闻的颜色过滤
def hot_news_filter(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""
