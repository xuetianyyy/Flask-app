from . import api_user
from flask import request, jsonify, session, current_app, g
from utils.response_code import RET
from ihome import redis_conn, db
from api_1_0.user.models import User
from sqlalchemy.exc import IntegrityError
import re
# 自定义的登录装饰器
from utils.commons import login_required
# 七牛云上传图片
from utils.image_storage import storage


# POST /api/1.0/user/register
@api_user.route('/register', methods=['POST'])
def register():
    """ 用户注册

    POST Request :
        需要携带的参数: 手机号, 短信验证码, 密码
        返回数据格式: json

    """
    # 获取请求的json数据, 返回字典
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    # 1.效验参数
    if not all([mobile, sms_code, password]):
        return jsonify(errcode=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'^1[3456789]\d{9}$', mobile):
        # 表示格式不对
        return jsonify(errcode=RET.PARAMERR, errmsg='手机号格式不正确')

    if password != password2:
        return jsonify(errcode=RET.PARAMERR, errmsg='两次输入的密码不一致')

    # 2. 从redis中取出短信验证码, 判断是是否过期
    try:
        real_sms_code = redis_conn.get('sms_code_{}'.format(mobile)).decode()
    except Exception as e:
        # 记录错误日志
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg='验证码读取异常')
    else:
        if real_sms_code is None:
            return jsonify(errcode=RET.NODATA, errmsg='短信验证码已过期')

    # 3. 判断用户填写短信验证码的正确性
    if real_sms_code != sms_code:
        return jsonify(errcode=RET.DATAERR, errmsg='短信验证码输入错误')

    # 4. 删除已经使用的短信验证码
    try:
        redis_conn.delete('sms_code_{}'.format(mobile))
    except Exception as e:
        current_app.logger.error(e)

    # 4. 判断用户的手机号是否注册过, 如未注册则保存数据到数据库中
    user = User(name=mobile, mobile=mobile)
    user.password = password
    try:
        # 因为mobile字段是唯一的, 如果用户提交的手机号被注册, 则会抛出异常
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 事务回滚
        db.session.rollback()
        # 记录错误日志, 该异常代表手机号出现重复(mobile字段)
        current_app.logger.error(e)
        return jsonify(errcode=RET.DATAEXIST, errmsg='该手机号已经注册')
    except Exception as e:
        # 数据库的其它异常
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg='数据库异常')

    # 5. 保存登录状态到session中
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    # 6. 返回结果
    return jsonify(errcode=RET.OK, errmsg='用户注册成功')


# POST /api/1.0/user/login
@api_user.route('/login', methods=['POST'])
def login():
    """ 用户登录

    POST Request :
        需要携带的参数: 手机号, 密码
        返回数据格式: json

    """
    # 1. 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    # 2. 效验参数
    if not all([mobile, password]):
        return jsonify(errcode=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'1[3456789]\d{9}', mobile):
        # 表示格式不对
        return jsonify(errcode=RET.PARAMERR, errmsg='手机号格式不正确')

    # 判断用户请求的次数有没有超过限制
    # 获取请求的地址, 和最大的登录错误次数限制
    user_ip = request.remote_addr
    login_error_max_nums = current_app.config.get('LOGIN_ERROR_MAX_NUMS')
    try:
        # 尝试获取用户redis中的请求次数记录
        request_nums = redis_conn.get('request_nums_{}'.format(user_ip))
    except Exception as e:
        current_app.logger.error(e)
    else:
        if request_nums is not None and int(request_nums.decode()) >= login_error_max_nums:
            return jsonify(errcode=RET.IPERR, errmsg='登录次数受限, 请于10分钟后再试')

    # 验证用户密码
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        jsonify(errcode=RET.DBERR, errmsg='获取用户信息失败')

    # 判断用户名和密码
    if user is None or not user.check_password(password):
        # 如果验证失败, 记录错误次数, 返回信息
        try:
            # 该方法会key的值累加1, 如果key不存在则自动创建并设置初始值为0
            redis_conn.incr('request_nums_{}'.format(user_ip))
            # 设置登录错误记录的过期时间为600/S
            redis_conn.expire('request_nums_{}'.format(user_ip), 600)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errcode=RET.DATAERR, errmsg='用户名或密码错误')

    # 3. 保存登录状态到session中
    if user.name is None:
        # 如果用户昵称未设置, 则使用手机号
        session['name'] = mobile
    else:
        session['name'] = user.name
        session['mobile'] = mobile
        session['user_id'] = user.id

    # 4. 返回结果
    return jsonify(errcode=RET.OK, errmsg='登录成功')


# GET /api/1.0/user/session
@api_user.route("/session", methods=['GET'])
def chek_login():
    """ 检查登录状态 """
    # 尝试从session中获取用户的名字
    name = session.get('name')

    # 如果session中的数据name名字存在, 则表示用户已经登录, 否则未登录
    if name is not None:
        return jsonify(errcode=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errcode=RET.SESSIONERR, errmsg='false')


# DELETE /api/1.0/user/session
@api_user.route("/session", methods=["DELETE"])
def logout():
    """ 登出 """
    # 清除session数据
    csrf_token = session.get('csrf_token')
    session.clear()
    session['csrf_token'] = csrf_token
    return jsonify(errcode=RET.OK, errmsg="退出成功")


# POST /api/1.0/user/portrait
@api_user.route('/portrait', methods=['POST'])
# 注意自定义登录装饰器应该放在最下面, 因为它应该最先被装饰
@login_required
def set_user_portrait():
    """ 设置用户头像

    Requst Param:
        file_data: 图片数据(多媒体表单上传)
    Returns:
        返回对应的状态码和错误信息

    """
    # 它在登录装饰器中, 已经获取并保存在g对象中, 所以我们可以直接从g对象中获取
    user_id = g.user_id

    # 获取图片
    image_file = request.files.get('image_file')

    if image_file is None:
        return jsonify(errcode=RET.PARAMERR, errmsg="缺少参数, 图片未上传")

    # 读取图片文件数据
    image_data = image_file.read()

    try:
        # 获取域名: 在配置文件中设置
        host = current_app.config.get('QINIU_ZONE_HOST')
        # 获取图片完整链接
        image_url = storage(host, image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.THIRDERR, errmsg="图片上传失败")

    # 保存图片链接到数据库中
    try:
        user = User.query.filter_by(id=user_id).update({'avatar_url': image_url})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="图片信息保存失败")

    # 保存成功返回
    return jsonify(errcode=RET.OK, errmsg="图片上传成功", image_url=image_url)


# POST /api/1.0/user/set-username
@api_user.route('/set-username', methods=['post'])
@login_required
def set_user_name():
    """ 设置用户名

    Requst Param:
        username: 用户名称
    Returns:
        返回对应的状态码和错误信息

    """
    req_dict = request.get_json()
    username = req_dict.get('username')

    # 效验参数
    if username is None:
        return jsonify(errcode=RET.PARAMERR, errmsg="缺少参数, 未设置用户名")

    # 尝试查询用户名是否存在
    try:
        user = User.query.filter_by(id=g.user_id, name=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

    # 判断用户名是否存在
    if user is not None:
        return jsonify(errcode=RET.DATAEXIST, errmsg="用户名已存在, 请重新设置")
    else:
        try:
            user = User.query.filter_by(id=g.user_id).update({'name': username})
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errcode=RET.DBERR, errmsg="用户名保存失败")

    # 保存成功返回
    return jsonify(errcode=RET.OK, errmsg="用户名设置成功")


# GET /api/1.0/user/get-user-msg
@api_user.route('/get-user-msg')
@login_required
def get_user_msg():
    """ 获取用户信息 """
    try:
        user = User.query.filter_by(id=g.user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    else:
        # to_dict()是在模型中封装的返回信息方法
        return jsonify(user.to_dict())


# GET /api/1.0/user/get-real-name
@api_user.route('/get-real-name')
@login_required
def get_real_name():
    """ 获取用户实名信息 """
    try:
        user = User.query.filter_by(id=g.user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

    # 返回用户实名信息, 其中auth_to_dict()是在模型类中封装的返回信息方法
    return jsonify(errcode=RET.OK, errmsg="获取成功", data=user.auth_to_dict())


# POST /api/1.0/user/set-real-name
@api_user.route('/set-real-name', methods=['POST'])
@login_required
def set_real_name():
    """ 设置用户实名认证

    Request Param:
        real_name:  用户的真实姓名
        id_card:    用户的身份证号
    Returns:
        对应的状态码和错误信息

    """
    req_dict = request.get_json()
    real_name = req_dict.get('real_name')
    id_card = req_dict.get('id_card')

    # 效验参数
    if not req_dict:
        return jsonify(errcode=RET.PARAMERR, errmsg="您没有提交信息, 请填写完整后提交")

    if not all([real_name, id_card]):
        return jsonify(errcode=RET.PARAMERR, errmsg="信息不全, 请填写完整后提交")

    # 效验数据格式
    if re.match(r"\d{17}[\dX]", id_card) is None:
        return jsonify(errcode=RET.PARAMERR, errmsg='身份证格式填写错误, 请填写18位的完整号码')

    # 只有当real_name, 和id_card为None的情况下, 才允许设置实名制, 否则不允许
    try:
        user = User.query.filter_by(id=g.user_id, real_name=None, id_card=None).update({'real_name': real_name, 'id_card': id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="身份信息保存失败, 或您已经过实名制")

    # 正确返回
    return jsonify(errcode=RET.OK, errmsg="实名提交成功, 请等待系统审核...")
