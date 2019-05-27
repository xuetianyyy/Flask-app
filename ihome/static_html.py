# from . import app_index, db
from flask import Blueprint, current_app, make_response
from flask_wtf import csrf
from api_1_0.user import models
from api_1_0.order import models
from api_1_0.house import models


# 提供静态页面蓝图
static_html = Blueprint('static_html', __name__)


@static_html.route('/', defaults={'html_file_path': ''})
@static_html.route('/<path:html_file_path>')
def index(html_file_path):
    """ 接收html文件的路径 """
    if not html_file_path:
        html_file_path = 'index.html'

    if html_file_path != 'favicon.ico':
        html_file_path = 'html/' + html_file_path

    # 创建一个csrf_token值
    csrf_token = csrf.generate_csrf()

    # 我们需要使用make_response将返回的静态页面, 封装在响应体里面, 得到响应对象
    resp = make_response(current_app.send_static_file(html_file_path))

    # 设置cookie值
    resp.set_cookie('csrf_token', csrf_token)

    return resp
