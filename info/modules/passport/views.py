# -*- coding: utf-8 -*-
# @Author:lecis
# @Time:2020/11/18 17:51
# @ Software:PyCharm
import json
import re
from ...libs.yuntongxun.sms import CCP

from flask import request, current_app, make_response, jsonify

from . import passport_blue

# 功能获取图片验证码
from ... import redis_store, constants
from ...utils.captcha.captcha import captcha


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
    # 2.校验参数，图片验证码
    redis_image_code = redis_store.get('image_code: %s' % image_code_id)
    # 和传递的图片验证码进行比较
    if image_code != redis_image_code:
        return jsonify(errno=10000, errmsg='图片验证码填写错误')
    # 3.校验参数，手机号格式
    if not re.match(r'1[3-9]\d{9}', mobile):
        return jsonify(errno=10000, errmsg='手机号格式错误')
    # 4.发送短信，调用封装好的cpp
    ccp = CCP()
    result = ccp.send_template_sms('18159661084', ['9999999', 5], 1)
    if result == -1:
        return jsonify(errno=30000, errmsg='验证码发送失败')
    return jsonify(errno=0, errmsg='验证码发送成功')
    # 5.返回发送的状态（成功或是失败）