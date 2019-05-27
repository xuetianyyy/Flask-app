from flask import Blueprint


api_house = Blueprint('api_house', __name__)


# 注册视图
from . import views
