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
from info import create_app, db, models  # 导入models是为了让整个应用程序知道有models的存在
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

# 调用方法，获取app
app = create_app('develop')

# 创建manager对象管理app
manager = Manager(app)

# 使用migrate关联app， db
Migrate(app, db)
# 给manager添加一条操作命令
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    # app.run()
    manager.run()