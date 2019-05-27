from . import db
from datetime import datetime


class BaseModel():
    """ 这是一个模型基类, 用于创建公共的字段 """
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
