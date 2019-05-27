import random
import re
from . import api
from utils.captcha.captcha import captcha
from ihome import redis_conn
from flask import current_app, jsonify, make_response, request
from utils.response_code import RET
from api_1_0.user.models import User
from libs.YunTongXun.SendTemplateSMS import CCP
from tasks.task_sms import send_sms


# GET /api/1.0/image_code/<image_code_id>
@api.route('/image_code/<image_code_id>')
def image_code(image_code_id):
    """ 获取图片验证码

    Args:
        image_code_id:   图片验证码编号
    Retruns:
        正常情况(验证码图片)  错误情况(错误信息)

    """
    # 1. 业务逻辑处理
    if not image_code_id:
        return jsonify(errcode=RET.NODATA, errmsg='缺少数据')

    # 2. 生成验证码图片
    name, text, image_data = captcha.generate_captcha()
    # print(text)

    # 将验证码真实值与编号保存到redis中, 使用字符串数据存储单条记录: 'image_code_编号': '验证码真实值'
    try:
        redis_conn.set('image_code_{}'.format(image_code_id), text, ex=current_app.config.get('IMAGE_CODE_REDIS_EXPIRE'))
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg='保存图片验证码失败')

    # 3. 返回图片
    resp = make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# GET /api/1.0/sms_code/<mobile>?image_code_id=xxx&image_code=xxx
@api.route('/sms_code/<mobile>')
def get_sms_code(mobile):
    """ 获取短信验证码
    Args:
        mobile: 注册人的手机号

    URL Param:
        image_code_id: 图片验证码id
        image_code   : 图片验证码

    Retruns:
        正常情况: 发送成功的json信息
        错误情况: 异常的json信息

    """
    # 1. 业务逻辑处理
    # 获取短信验证码的过期时间
    sms_code_redis_expire = current_app.config.get('SMS_CODE_REDIS_EXPIRE')
    if sms_code_redis_expire % 60 != 0:
        return jsonify(errcode=RET.PARAMERR, errmsg='短信验证码过期时间不合法, 需为60的整除数')

    # 效验参数是否缺失
    image_code_id = request.args.get('image_code_id')
    image_code = request.args.get('image_code')
    if not all([mobile, image_code_id, image_code]):
        return jsonify(errcode=RET.PARAMERR, errmsg='参数不全')

    # 效验手机号是否合法
    res = re.match(r"^1[3456789]\d{9}$", mobile)
    if res is None:
        return jsonify(errcode=RET.DATAERR, errmsg='非法数据, 不是合法的手机号')

    # 效验图片验证码是否正确, 从redis中取出真实的验证码, 与用户输入的值对比
    try:
        real_image_code = redis_conn.get('image_code_{}'.format(image_code_id))
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg='读取Redis数据库异常')

    # 判断图片验证码是否过期
    if real_image_code is None:
        return jsonify(errcode=RET.NODATA, errmsg='图片验证码已失效, 请点击更换重试')

    # 对比验证码
    if real_image_code.decode().lower() != image_code.lower():
        # 表示用户填写错误
        return jsonify(errcode=RET.DATAERR, errmsg='图片验证码错误')

    # 删除已经使用的验证码, 防止对同一个验证码进行多次验证
    try:
        redis_conn.delete('image_code_{}'.format(image_code_id))
    except Exception as e:
        # 记录错误日志, 这里只是一个逻辑操作, 不要提前返回
        current_app.logger.error(e)

    # 判断用户在短时间内是否发送过验证码, 如60s内, 如果有发送记录, 则在规定时间内不允许发送第二次
    try:
        send_sign = redis_conn.get('send_sms_code_{}'.format(mobile))
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(e)
    else:
        if send_sign is not None:
            # 表示用于在短时间内有发送短信的记录, RET.REQERR = "4201"
            return jsonify(errcode=RET.REQERR, errmsg='请求次数受限, 请于60秒后发送')

    # 判断手机号是否已存在, 如果不存在, 则生成短信验证码, 发送短信
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        # 记录错误日志, 这里不能return终止, 因为可能会出现用户信息正确, 但数据库异常的情况, 此时应该让用户继续注册
        current_app.logger.error(e)
    else:
        if user is not None:
            # 表示手机号已存在
            return jsonify(errcode=RET.DATAEXIST, errmsg='该手机号已经注册')

    # 设置短信验证码, 并保存在redis中
    sms_code = '{0:0>6}'.format(random.randint(0, 999999))
    try:
        # 在redis保存字符串数据
        redis_conn.set('sms_code_{}'.format(mobile), sms_code, ex=sms_code_redis_expire)
        # 保存发送短信的手机号记录, 防止用户在短时间内(如60s)执行重复发送短信的操作
        redis_conn.set('send_sms_code_{}'.format(mobile), 'yes', ex=current_app.config.get('SEND_SMS_CODE_INTERVAL'))
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg='短信验证码保存异常')

    # 保存短信验证码到redis中: 手机号(key): 验证码(value) 字符串类型
    # ccp = CCP()
    # result = ccp.sendTemplateSMS(mobile, [sms_code, str(sms_code_redis_expire / 60)], '1')
    # if result == 0:
    #     # 发送成功
    #     return jsonify(errcode=RET.OK, errmsg='短信发送成功')
    # else:
    #     return jsonify(errcode=RET.THIRDERR, errmsg='短信发送失败, 第三方错误')

    # 使用celery进行异步请求, 发送短信
    send_sms.delay(mobile, [sms_code, str(sms_code_redis_expire / 60)], '1')

    # 因为selery是异步操作的, 它的执行不会对这里产生阻塞, 所以我们设想, 只要发送了, 就代表成功了
    return jsonify(errcode=RET.OK, errmsg='短信发送成功')
