from datetime import timedelta
import redis


class Config():
    """ 配置信息的基类 """
    # 设置session的秘钥, 同是crsf验证也依赖于它
    SECRET_KEY = '$&_p%ise9)wf=$mehhy8fw167!#+d4vcv^^r^kijm)+(yw3gq2'
    # 配置Mysql数据库, 'mysql://用户名:密码@地址:端口/数据库名'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:xxxxxxxx@127.0.0.1:3306/ihome_demo'
    # 设置模型类与数据表同步跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 查询时会显示原始SQL语句
    # SQLALCHEMY_ECHO = True

    # redis配置
    REDIS_HOST = '127.0.0.1'    # redis地址
    REDIS_PORT = 6379           # reids端口
    REDIS_DB = 6                # redis数据库编号

    # Flask-Session配置
    # 指定要使用的会话接口的类型, 可以是redis, mongodb, sqlalchemy等...
    SESSION_TYPE = 'redis'
    # 注意它必须是一个Redis连接的实例，默认连接到127.0.0.1:6379
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    # 是否对session_id进行混淆, 如果为True, 则必须配置SECRET_KEY秘钥(依赖于它)
    SESSION_USE_SIGNER = True
    # 设置session的过期时间, 它可以设置detetime对象的时间, 或表示秒数的整数, 例如: 3600, 默认永久有效
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

    # 设置图片验证码的过期时间/秒
    IMAGE_CODE_REDIS_EXPIRE = 100
    # 设置短信验证码的过期时间/秒, 注意: 只能设置60的倍数
    SMS_CODE_REDIS_EXPIRE = 120
    # 用户发送短信验证码的间隔时间/秒, 防止在短时间内重复发送短信
    SEND_SMS_CODE_INTERVAL = 60
    # 用户最大的登录错误次数限制
    LOGIN_ERROR_MAX_NUMS = 5

    # 七牛云存储相关配置,空间域名
    QINIU_ZONE_HOST = 'http://image.weidong168.com'

    # 设置获取房源信息的redis缓存时间, 单位/秒
    AREA_INFO_REDIS_CACHE_EXPIRES = 3600 * 2
    # 设置首页幻灯片, 热门房源, 以及房屋详情信息的redis缓存时间, 单位/秒
    HOME_PAGE_DATA_REDIS_EXPIRES = 3600 * 3
    # 设置搜索列表的缓存过期时间/秒
    HOUSE_SEARCH_LIST_EXPIRES = 3600 * 1.5
    # 获取房屋详情的评论数量
    HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 10
    # 设置房屋列表, 每页展示的房屋查询数量
    HOUSE_LIST_PER_PAGE = 10

    # 支付宝网关, 这里是用户需要跳转支付的链接前缀(注意: 这里设置的是沙箱环境)
    ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'


class DevelopmentConfig(Config):
    """ 用于开发模式的配置信息 """
    # 开启调试模式
    DEBUG = True


class ProductionConfig(Config):
    """ 用于生产模式的配置信息 """
    pass


# 提供给app对象的配置映射
config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig,
}
