# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/21 11:47
# @ Software:PyCharm
from flask import Blueprint

news_blue = Blueprint('news', __name__, url_prefix='/news')

from . import views