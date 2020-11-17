# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 23:26
# @ Software:PyCharm
from flask import Blueprint

# 1.创建蓝图对象
index_blue = Blueprint('index', __name__)

# 2.导入views文件装饰视图函数
from . import views