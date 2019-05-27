from config import config_map       # 导入配置映射对象
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_wtf import CSRFProtect
import redis
import logging
from logging.handlers import RotatingFileHandler


# 创建SQLAlchemy数据库工具对象
db = SQLAlchemy()


# 定义一个空的redis连接对象, 它最终会在create_app方法中重新被定义, 因为此时无法获取app对象
redis_conn = None

# 为flask增加csrf防护
csrf = CSRFProtect()


# 设置日志的记录等级, 以logging对象的方式设置
logging.basicConfig(level=logging.DEBUG) 	# 可以是: ERROR, WARN, INFO, DEBUG的其中一个
# 创建日志记录器, 参数1: 指明日志保存的路径, 参数2: 每个日志文件的最大大小(这里为30MB), 参数3: 保存的日志文件个数上限
# 当日志的文件的大小超过maxBytes指定的大小后, 就会重新创建一个新的日志文件, 但它只会保留最新backupCount指定个数的文件, 更早的则被清理
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024 * 1024 * 30, backupCount=10)
# 创建日志记录的格式, 它们分别表示: 日志等级, 输入日志信息的文件名, 行数, 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象(flask app)添加日志记录器
logging.getLogger().addHandler(file_log_handler)


# 创建工厂模式的app对象
def create_app(config_name):
    """
    创建flask的应用对象(工厂模式)
    :param config_name: str  配置模式的名字  可以是('develop' 或 'product')
    :return: app对象
    """
    app = Flask(__name__)
    # 加载配置文件
    app.config.from_object(config_map.get(config_name))

    # 使用app对象对SQLAlchemy实例进行初始化
    db.init_app(app)

    # 使用app对象对csrf进行初始化
    csrf.init_app(app)

    # 创建redis连接对象, 并设置为全局对象
    global redis_conn
    redis_conn = redis.StrictRedis(host=app.config.get('REDIS_HOST'),
                                   port=app.config.get('REDIS_PORT'),
                                   db=app.config.get('REDIS_DB')
                                   )

    # 利用flask-session将session数据保存到redis中
    Session(app)

    # 蓝图板块
    from api_1_0.public import api
    from api_1_0.house import api_house
    from api_1_0.order import api_order
    from api_1_0.user import api_user
    from .static_html import static_html

    # 注册蓝图
    app.register_blueprint(api, url_prefix='/api/1.0')
    app.register_blueprint(api_house, url_prefix='/api/1.0/house')
    app.register_blueprint(api_order, url_prefix='/api/1.0/order')
    app.register_blueprint(api_user, url_prefix='/api/1.0/user')
    app.register_blueprint(static_html)

    return app
