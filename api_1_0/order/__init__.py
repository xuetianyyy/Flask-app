from flask import Blueprint


api_order = Blueprint('api_order', __name__)


# 提交视图
from . import views, alipay
