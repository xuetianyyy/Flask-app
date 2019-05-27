from flask import session, jsonify, g
from .response_code import RET
# 这是python的标准模块, 专门提供函数的工具
import functools


# 自定义验证登录状态装饰器
def login_required(view_func):
    """ 登录验证装饰器

    如果验证成功, 则执行视图函数, 否则, 返回json错误信息, 提示用户未登录
    """
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        # 判断用户的登录状态
        user_id = session.get('user_id')

        # 如果用户是登录的, 执行视图函数
        if user_id is not None:
            # 将user_id保存到g对象中, 在视图函数中可以通过g对象获取保存的数据
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 如果未登录, RET.返回 SESSIONERR = "4101"
            return jsonify(errcode=RET.SESSIONERR, errmsg="用户未登录")

    return wrapper
