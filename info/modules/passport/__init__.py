# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/18 17:49
# @ Software:PyCharm
from flask import Blueprint

# 创建蓝图对象
passport_blue = Blueprint('passport', __name__, url_prefix='/passport')

# 导入views装饰视图函数
from . import views