# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/23 9:56
# @ Software:PyCharm
from . import profile_blue
from flask import render_template


@profile_blue.route('/user_index')
def user_index():
    return render_template("news/user.html", data={})