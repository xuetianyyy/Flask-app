from flask import Blueprint


api = Blueprint('api', __name__)


# 提交视图
from .views import image_code
