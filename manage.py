# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/17 20:58
# @ Software:PyCharm
"""
相关配置信息
1.数据库配置
2.redis配置
    缓存访问频率高的内容，存储session信息，图片验证码，短信验证码
3.session配置
    将来用来保存用户的登录信息
4.csrf配置
    保护app防止csrf攻击
    校验的请求方式：'POST', 'PUT', 'PATCH', 'DELETE'
"""
from info import create_app

# 调用方法，获取app
app = create_app('develop')


if __name__ == "__main__":
    app.run()