from flask import Blueprint


api_user = Blueprint('api_user', __name__)


# 添加视图
from . import views
