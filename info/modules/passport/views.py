# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/18 17:51
# @ Software:PyCharm
import json
import re
import random
from ...libs.yuntongxun.sms import CCP

from flask import request, current_app, make_response, jsonify

from . import passport_blue


from ... import redis_store, constants, db
from ...models import User
from ...utils.captcha.captcha import captcha


from ...utils.response_code import RET


# 功能获取图片验证码
# 请求路径： /passport/imag_code
# 请求方式: GET
# 携带参数： ur_id,pre_id
# 返回值: 图片
@passport_blue.route('/image_code')
def image_code():

    # 1.获取前端传递的参数
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')

    # 2.调用generate_captcha获取验证码的编号，值，图片（二进制图片）
    name, text, image_data = captcha.generate_captcha()

    # 3.将图片验证码的值保存在Redis
    try:
        # 参数1：key, 参数2：value， 参数3：有效期
        redis_store.set("image_code: %s" % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

        # 4.判断是否有上一次的图片验证码
        if pre_id:
            redis_store.delete("image_code: %s" % pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return '图片验证码操作失败'
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response


# 获取短信验证码
# 请求路径：/passport/sms_code
# 请求方式：POST
# 请求参数：mobile, image_code, image_code_id
# 返回值：errno, errmso
@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    # 1.获取参数
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get('mobile')
    image_code = dict_data.get('image_code')
    image_code_id = dict_data.get('image_code_id')

    # 2.参数的为空校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 3.校验手机格式
    if not re.match(r'1[3-9]\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')

    # 4.通过图片验证码编号获取图片验证码
    try:
        redis_image_code = redis_store.get("image_code: %s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='操作redis失败')

    # 5.判断图片验证码是过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg='图片验证码过期')

    # 6.判断图片验证码是否正确
    if image_code.lower() != redis_image_code.lower():
        return jsonify(errno=RET.DBERR, errmsg='图片验证码错误')

    # 7.删除redis中的图片验证码
    try:
        redis_store.delete("image_code: %s" % image_code_id)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg='redis删除图片验证码失败')
    # 8.生成一个随机的短信验证码，调用ccp发送短信，判断是否发送成功
    sms_code = "%06d" % random.randint(0, 999999)
    # 先不发短信，直接后台获取，免得没钱了
    current_app.logger.debug("短信验证码是 = %s" % sms_code)
    # cpp = CCP()
    # result = cpp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
    # if result == -1:
    #     return jsonify(errno=RET.DATAERR, errmsg='短信验证码发送失败')
    # 9.将短信保存在redis中
    try:
        redis_store.set("sms_code: %s" % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码保存到redis失败')
    # 10.返回响应
    return jsonify(errno=RET.OK, errmsg='短信发送成功')
# "sms_code: 18159661084"


# 1.注册用户
# 2.请求路径：/passport/register
# 3.请求方式：POST
# 4.请求参数：mobile，sms_code,password
# 5.返回值：errno, errmsg
@passport_blue.route('/register', methods=['POST'])
def register():
    # 1.获取参数
    json_data = request.data
    dict_data = json.loads(json_data)
    mobile = dict_data.get('mobile')
    sms_code = dict_data.get('sms_code')
    password = dict_data.get('password')

    # 2.参数的为空校验
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 3.根据手机号作为key取出redis中的验证码
    try:
        redie_sms_code = redis_store.get("sms_code: %s" % mobile)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码取出失败")

    # 4.判断短信验证码是否过期
    if not redie_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码已经过期")

    # 5.判断短信验证码是否正确
    if sms_code != redie_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码填写错误")
    # 6.删除短信验证码
    try:
        redis_store.delete("sms_code: %s" % mobile)
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码删除失败")

    # 7.创建用户对象
    user = User()

    # 8.设置用户对象的属性
    user.nick_name = mobile
    user.password_hash = password
    user.mobile = mobile
    user.signature = "该用户很懒，什么都没写"

    # 9.保存用户到数据库中
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger(e)
        return jsonify(errno=RET.DATAERR, errmsg="用户注册失败")

    # 10.返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")