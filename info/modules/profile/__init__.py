# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/23 9:54
# @ Software:PyCharm
from flask import Blueprint

# 创建用户蓝图对象
profile_blue = Blueprint('profile', __name__, url_prefix='/user')

# 装饰视图函数
from . import views