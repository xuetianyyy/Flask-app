**项目目录列表**

+ [项目介绍](#项目介绍)
+ [配置文件config.py](#配置文件config.py)
+ [启动文件manage.py](#启动文件manage.py)
+ [首页](#首页)
+ [注册及登录](#注册及登录)
  + [注册](#注册)
  + [登录](#登录)
+ [个人页](#个人页)
  + [个人主页](#个人主页)
  + [个人信息修改](#个人信息修改)
  + [实名认证](#实名认证)
  + [我的房源-作为房东可发布](#我的房源-作为房东可发布)
  + [发布新房源-房源信息提交页](#发布新房源-房源信息提交页)
+ [搜索列表页](#搜索列表页)
+ [房屋详情页](#房屋详情页)
+ [房屋预定-订单创建页](#房屋预定-订单创建页)
+ [我的订单-基于客户](#我的订单-基于客户)
+ [客户订单-基于房东](#客户订单-基于房东)
+ [订单支付及评论](#订单支付及评论)
+ [其它说明](#其它说明)

----



#  项目介绍

该项目基于Vue作为前端, Flask作为服务端的前后端分离项目, 在项目中使用Mysql作为数据库, Redis作为缓存, 以及容联云作为第三方发送短信验证码(为避免阻塞, 其发送的任务由Celery异步执行), 其次还使用了七牛云作为图片文件的存储服务

在该项目中, 前端部分, 区域选项, 以及日期选项插件, 我基于Mui进行了二次封装,  其次, 还原生封装了一些项目中需要用到的方法, 如提取页面来源路径, 提取Cookie字段, 日期计算, Url查询参数提取等...

后端部分, 由于容联云官方提供的接口是Python2.7版本的源码,  而我项目使用的是Python3.6版本, 所以我对容联云的接口, 进行了改写, 并进一步进行了封装, 其次还有生成图片验证码的接口, 这里就不详细概述了...

整个项目所有的后端接口, 我使用Flask的蓝图, 将其划分为了四块, public(这是公共API, 主要实现验证码的方法), user(所有关于用户操作的行为API, 以及Model类都在这里实现的),  house(所有对房屋的展示, 操作, 以及模型类都在这里实现) , order(关于订单的操作, 以及模型类, 其次这里还是先了支付宝的支付及交易查询接口)

前端所有带有包体的请求数据, 都规定以json格式进行发送, 后端所有的API同样以json格式返回数据(其中包含响应码, 响应信息, 以及响应数据)



**项目结构:**  

> @在/directory.txt文件中

**项目依赖:**

> @在/py-dependent.txt中已经写入

您可以使用该命令安装所有依赖: `pip3 install -r py-dependent.txt`



**项目启动方式:**

进入项目根目录执行: `python3 manage.py runserver`

进入项目根目录执行启动Celery任务: `celery -A tasks.task_sms worker -l info`



**如果要正常运行该项目, 您必须要修这些配置:**

1. 在/config.py中, 修改以下必须的配置项

``` python
# 配置Mysql数据库, 'mysql://用户名:密码@地址:端口/数据库名'
SQLALCHEMY_DATABASE_URI = 'mysql://root:xxxxxxxx@127.0.0.1:3306/ihome_demo'

# redis配置
REDIS_HOST = '127.0.0.1'    # redis地址
REDIS_PORT = 6379           # reids端口
REDIS_DB = 6                # redis数据库编号

# 七牛云存储相关配置,空间域名
QINIU_ZONE_HOST = 'http://image.weidong168.com'  # 改为您自己的空间域名
```

2. 在/utls/image_storage.py中修改您的七牛云(Access Key, Secret Key 和 对象存储空间名

``` python
# 需要填写你的 Access Key 和 Secret Key
access_key = '填写你的Access Key'
secret_key = '填写你的Secret Key'

# 构建鉴权对象
q = Auth(access_key, secret_key)

# 要上传的空间
bucket_name = '填写你的对象存储空间名'
```

3. 在/libs/YunTongXun/SendTemplateSMS.py中修改以下参数

``` python
accountSid = '开发者主账号ACCOUNT SID'

# 说明：主账号Token，登陆云通讯网站后，可在控制台首页中看到开发者主账号AUTH TOKEN
accountToken = '开发者主账号AUTH TOKEN'

# 请使用管理控制台中已创建应用的APPID, 注意: 测试环境只能使用未上线的应用
appId = '应用的APPID'
```

----



# 配置文件config.py

``` python
from datetime import timedelta
import redis


class Config():
    """ 配置信息的基类 """
    # 设置session的秘钥, 同是crsf验证也依赖于它
    SECRET_KEY = '$&_p%ise9)wf=$mehhy8fw167!#+d4vcv^^r^kijm)+(yw3gq2'
    # 配置Mysql数据库, 'mysql://用户名:密码@地址:端口/数据库名'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:xxxxxxx@127.0.0.1:3306/ihome_demo'
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
```



----




# 启动文件manage.py

**app对象的抽离, 定义在主模块的初始化文件中:**

``` python
### /ihome/__init__.py

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
logging.basicConfig(level=logging.DEBUG) 	
# 设置日志文件的容量
file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024 * 1024 * 30, backupCount=10)
# 创建日志记录的格式, 它们分别表示: 日志等级, 输入日志信息的文件名, 行数, 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象(flask app)添加日志记录器
logging.getLogger().addHandler(file_log_handler)


# 创建工厂模式的app对象
def create_app(config_name):
    """ 创建flask的应用对象(工厂模式)
    
    Args:
    	config_name: str  配置模式的名字  可以是('develop' 或 'product')
    				该参数决定了项目的运行环境
    Returns: 
    	app对象
    	
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
```



**启动文件manage.py**

``` python
from ihome import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


# 需要传递一个工作环境的参数
app = create_app('develop')
manager = Manager(app)

# 创建Migrate执行对象
Migrate(app=app, db=db)
# 添加迁移的脚本命令
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # print(app.url_map)
    manager.run()
```



----


# 首页

![](http://image.weidong168.com/ihome_index.jpg)

####  1. 前端部分

主要文件: 

| Path               | File       |
| :----------------- | :--------- |
| /ihome/static/html | index.html |
| /ihome/static/js   | inde.js    |

由于首页以展示为主, 所以下面的方法大多是在页面初始化的时候, 向后端发送的请求

1. 页面初始化, 获取用户登录状态, 该方法定义在getUserLogin()中, , 如果用户已登录, 则显示欢迎语, 及个人中心页面的kyrl\链接,  如未登录, 则显示注册和登录选项按钮
2. 获取首页轮播需要使用的幻灯片, 该方法定义在getUserLogin()中, 它主要是对当前最热门的房屋资源进行展示
3. 设置首页轮播, 该方法定义在setSlider()中, 由于时间问题, 我在该方法里用12行代码写了一个简易轮播, 我知道这并不够美观....
4. 获取用户搜索可选的城区信息列表, 该方法定义在getMyHouse(), 用于区域选择的选项列表展示
5. 封装区域选项, 以及日期选项的插件方法, 用于页面效果展示, 该方法定义在了showArea()和showDate()中
6. 定义搜索按钮触发的事件, 该方法定义在了searchHouse()中, 它会跳转到搜索列表页面, 同时在URL中提供相关的查询参数,, 如: 区域id, 入住日期...

---

####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
| ----------------------------------------- | ---------------------------------------------------- |
| ihome.api_1_0.user.views.chek_login       | 检查用户登录状态                                     |
| ihome.api_1_0.hosue.views.get_house_index | 获取最热门的前几个房屋信息, 返回给客户端(幻灯片所用) |
| ihome.api_1_0.hosue.views.get_area_info   | 获取业务范围内的所有城区信息列表                     |

**接口一get_house_index:**

为前端提供当前订单量最多的5个热门房屋信息, API地址: GET /api/1.0/house/index 这也是轮播需要的

该视图函数会先尝试从reids中读取缓存, 如果缓存信息存在, 则返回缓存信息, 如果缓存信息不存在, 则查询数据库, 根据订单量进行降序排序, 再使用limit函数取出前五条查询集(该数量提供了一个变量, 是可以修改的), 取出数据后, 则将该数据存储在redis中(同时为该缓存设置了过期时间, 因为热门的房屋是会改变的, 该时间在配置文件中提供了一个常量可以修改), 然后将查询集返回给客户端(在这里, 我在模型类中封装了一个house.to_full_dict()方法, 用于将房屋的基本信息, 转为字典对象, 那么可以通过这个方法, 直接将字典数据返回给客户端)

**接口二get_area_info:**

提供所有业务范围的城区列表, API地址: GET /api/1.0/house/get-area-info  这是区域选项所需要的

该视图函数会先尝试从reids中读取缓存, 如果缓存信息存在, 则返回缓存信息, 如果缓存信息不存在, 则查询数据库, 取出所有的区域信息数据后, 则将该数据存储在redis中(同时为该缓存设置了过期时间, 因为随着业务范围的扩展, 业务范围的区域可能会更新, 如果不设置过期时间, 那么给前端返回的永远都是过去的记录, 该时间在配置文件中提供了一个常量可以修改), 然后将查询集返回给前端

----



# 注册及登录

![](http://image.weidong168.com/ihome_re_login.jpg)



## 注册

#### 1. 前端部分

主要文件:

| Path               | File          |
| ------------------ | ------------- |
| /ihome/static/html | register.html |
| /ihome/static/js   | register.js   |

**图片验证码**

一: 由客户端生成一个图片验证码的ID(调用generateUUID()方法), 作为后端图片验证码存储的依据(key的一部分), 另外将该ID保存在一个全局变量中(data属性), 以便在获取短信验证码时, 使用该ID作为key来获取缓存中的真实图片验证码与客户端输入的验证码进行对比

二: 拼接图片验证码请求的URL(调用generateImageCode()方法)

三: 发送Ajax请求, 向服务端提供图片验证码的ID, 该ID作为路径参数传递, 如: /api/1.0/image_code/<image_code_id>, 同时以该API作为图片验证码的路径, 设置在页面中展示(因为该API返回的是生成验证码的图片数据)

**短信验证码**

当发送按钮触发sendSMSCode()事件后, 开始向服务端发送短信验证码的请求, 如果后端返回正确的响应码(errcode=='0')时, 代码验证码发送成功, 此时我们将验证码按钮设置为倒计时60秒, 之后才可以进行第二次发送, 因为这样可以防止用户重复的请求验证码, 如果发送失败, 则根据服务端返回的错误信息, 提示用户失败的原因

**立即注册**

当用户触发此事件后, 便向服务端提供所有的注册信息

一: 使用Vue的双向数据流, 绑定页面中所有的input元素, 获去所有的用户输入数据

二: 定义一个焦点离开事件, 用于检测用户输入的数据是否为空, 反之在对应的输入框下给出友情提示

三: 点击获取短信验证码, 至于获取过程可以看**短信验证码**的介绍, 另外, 在发送请求之前, 我们还会验证手机号是否合法, 还有拿到缓存的中的真实图片验证码与用户输入的图片验证码进行效验, 判断图片验证码是否正确, 之后再进入手机验证码的设置与操作, 如上面所介绍

四: 发送所有用户输入的信息, 提交给后端

----

####  2. 后端部分

API视图函数介绍:

| Views                                   | Description                                      |
| --------------------------------------- | ------------------------------------------------ |
| ihome.api_1_0.public.views.image_code   | 设置图片验证码在缓存中, 并向客户端返回验证码图片 |
| ihome.api_1_0.public.views.get_sms_code | 向用户的手机发送验证码, 并保存在缓存中           |
| ihome.api_1_0.user.views.register       | 用户注册逻辑实现                                 |

**接口一image_code:**

1. 获取客户端路径参数中的验证码ID
2. 使用封装的方法, 生成图片验证码
3.  将该客户端传递过来的ID作为验证码的key在Redis缓存中临时保存,
4. 后向客户端返回验证码图片

**接口二get_sms_code: ** 

1. 在配置文件中设置短信验证码的过期时间, 在该视图中获取, 并进行效验
2. 获取参数, 用户手机号, 输入的图片验证码, 及对应的图片验证码ID
3. 效验参数是否完整, 和参数是否合法(手机号)
4. 以用户传递过来的ID作为key从Reids中读取临时保存的真实图片验证码, 将其保存在一个变量中
5. 判断图片验证码是否过期(是否为空), 如过期则提前返回
6. 效验图片验证码是否正确, 将Redis中取出的图片验证码, 与用户输入的验证码进行对比
7. 删除已经使用过的验证码(第四步已经保存过), 避免用户对同一验证码进行多次验证, 浪费内存开销
8. 判断用户在短时间内是否发送过验证码(如60s), 如果有发送过, 则不允许进行发送第二次, 返回错误信息
9. 判断用户的手机号是否存在, 在用户表中查询该手机号的记录, 如果存在则提前返回
10. 设置自定义的验证码, 保存在在redis中, 以'sms_code_{手机号}'作为key保存string数据, 同时还要保存一个发送验证码的标记, 来记录该用户是否在短时间内发送过验证码, 该记录会随验证码一期过期, 因为在第**5**步中, 需要查询验证码是否过期
11. 使用Celery执行任务, 向用户发送短信
12. 向客户端返回成功的状态信息, 需要注意的是, 因为Celery执行任务是异步的, 它不会对它之后的代码产生阻塞, 所以在这里我们都假想只要用户发送了验证码, 就代表发送成功, 如果用户未收到验证码, 在没有错误信息返回的情况下, 用户只有进行再次发送验证码

**接口三register:**

1. 获取客户端发送过来的json数据, 并接收其中的参数, 包括(手机号, 短信验证码, 与两次输入的密码)
2. 效验参数的完整性, 如不完整则提前返回
3. 效验手机号是否合法
4. 效验用户两次输入的密码是否一致
5. 从redis读取短信验证码, 并判断是否过期, 如过期不存在则提前返回错误信息
6. 将Redis中的短信验证码, 与客户输入的验证码进行对比, 判断用户填写是否正确
7. 删除Redis中已经使用过的旧验证码, 防止用户对统一验证码进行多次验证
8. 判断用户填写的手机号是否注册过, 从用户表中查询该字段, 如有则提前返回
9. 对用户的密码进行加密并保存在在数据库中, 这里我在模型类总封装了一个password方法, 其中使用了werkzeug.security.generate_password_hash方法对密码进行加密, 并将该封装的方法转为一个类属性, 其后直接设置该属性即可对密码进行算法加密
10. 保存用户状态到session中, 记录用户登录
11. 返回注册成功的json信息给客户端

----



## 登录

#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | login.html |
| /ihome/static/js   | login.js |

1. 使用双向数据, 绑定表单输入框(手机号与密码), 获取用户输入信息
2. 输入效验, 验证手机号是否合法, 验证密码是否为空, 这在一个焦点离开事件中完成isInputData()
3. 用户登录触发, 设置请求头, 请求体, 向服务端发送登录请求, 得到响应码, 如果状态成功, 则跳转到首页, 否则弹出错误信息


----


#### 2. 后端部分

API视图函数介绍:

| Views                          | Description |
| ------------------------------ | ----------- |
| ihome.api_1_0.user.views.login | 用户登录    |

1. 获取参数(手机号, 密码)
2. 效验参数完整性
3. 效验手机号合法性(如格式)
4. 判断用户登录错误次数有没有超过限制(这在配置参数中有预留属性), 如有超过, 则限制十分钟后可再次登录
5. 使用在模型中封装的check_password方法判断用户输入的明文密码, 与数据库中保存的加密密码的值是否一致
6. 保存用户登录状态到session中(用户名, 手机号, 及用户ID)
7. 附加内容, 登录验证, 为了后续可以直接对视图进行验证用户登录状态, 所以这里我在ihome.utls.commons中封装了一个验证登录的装饰器login_required在该装饰器中, 我从session中获取到用户登录后存储的user_id, 并将它保存在flask全局对象g对象中, 并返回视图函数, 如果session中无法获取user_id证明用户并未登录, 此时返回未登录的状态码及错误信息给客户端

----



# 个人页

![](http://image.weidong168.com/ihome_personage1.jpg)

![](http://image.weidong168.com/ihome_personage2.jpg)



## 个人主页

#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | my.html |
| /ihome/static/js   | my.js |

1. 页面初始化时, 向服务端发送Ajax请求, 获取用户信息, 并将其替换到页面上对应的元素中
2. 定义用户退出触发的事件, 向服务端发送退出请求


----


####  2. 后端部分

API视图函数介绍:

| Views                                 | Description        |
| ------------------------------------- | ------------------ |
| ihome.api_1_0.user.views.get_user_msg | 获取用户的基本信息 |

1. 使用自定义的登录验证装饰器, 验证用户登录状态
2. 如已登录, 则从g对象中获取user_id然后根据该id在user表中查询出用户信息
3. 根据该查询的对象, 调用模型类中封装的to_dict()方法, 将用户信息转为字典对象, 返回给客户端

----



## 个人信息修改
#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | profile.html |
| /ihome/static/js   | profile.js |

1. 获取用户上传的多媒体表单文件(image), 这里是从多媒体表单的files属性中获取到文件内容, 然后将文件添加到FormData()对象的实例中 , 将其打包成表单数据, 以便发送给服务端
2. 发送POST请求, 将获取到用户上传的头像文件, 发送给服务端
3. 在Ajax的回调函数中, 接收状态码, 如果是4101则代表用户未登录, 将跳转到登录页面, 如果是0则代表上传成功, 此时将页面中预留的用户头像, img标签的src属性, 替换为服务端返回的头像链接地址, 其它情况则弹出错误信息
4. 设置用户名, 定义在setUsername()函数中, 使用双向数据绑定文本输入框, 获取用户输入的用户名信息, 向后端发送Ajax请求, 提交用户设置的用户名信息, 在该请求的回调函数中, 根据返回的状态码, 确认设置是否成功, 如果设置成功, 则弹出成功信息, 并设置1.5s定时器, 跳转到个人页面(当然, 这只是我个人做法)


----


####  2. 后端部分

API视图函数介绍:

| Views                                      | Description  |
| ------------------------------------------ | ------------ |
| ihome.api_1_0.user.views.set_user_portrait | 设置用户头像 |
| ihome.api_1_0.user.views.set_user_name     | 设置用户名   |

**接口一set_user_portrait:**

1. 验证用户登录(使用自定义验证装饰器)
2. 从g对象中获取user_id
3. 获取客户端发送过来的图片文件, 使用request.files.get()
4. 效验图片文件参数, 是否缺省
5. 读取图片文件, 获得该文件的二进制数据
6. 调用方法上传图片文件到七牛云中,并接收返回的图片链接, 该方法封装在utils.image_storage.storage中, 并返回上传图片的完整链接
7. 保存图片链接到数据中, 在User的模型中, 有一个avatar_url属性, 存储该数据
8. 返回上传成功状态码及状态信息, 以及上传图片的链接给客户端

**接口二set_user_name:**

1. 接收参数username
2. 效验参数是否缺失
3. 查询用户名是否存在, 如存在则提前返回状态信息, 如不存在则将用户名更新到User表中
4. 如无误, 则返回设置成功的状态信息给客户端

----



## 实名认证
#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | auth.html |
| /ihome/static/js   | auth.js |

**页面初始化, 获取用户实名认证信息:**

1. 该方法定义在getRealName()中
2. 在data中定义两个属性, 使用双向数据绑定页面输入框, 动态的获取(更新)输入框信息
3. 发送请求到服务端, 获取用户认证信息, 根据返回的状态码, 判断用户是否登录, 如未登录则直接跳转到登录页面
4. 如已登录, 则根据操作成功的状态码, 获取返回的信息, 并将其更新在双向数据的属性中(它会自动同步到页面)
5. 判断双向数据属性中是否为空值, 如果不为空值, 说明用户之前已经设置过实名信息, 此时则禁用所有输入框输入, 以及按钮的操作, 以展示用户实名信息为主, 如果该属性为空, 则说明用户之前没有绑定过, 则将页面所有表单操作设置为默认状态, 待用户输入
6. 同时在页面中, 我们应该友情的提示用户, 该资料非常重要, 请谨慎填写
7. 如果出现其它情况, 则向客户端弹出异常信息

**设置用户实名信息:**

1. 作为提交按钮的触发事件, 定义在setRealName()方法中
2. 设置请求体, 将用户输入的实名信息, 绑定进来
3. 验证身份证号码格式是否正确, 使用正则
4. 发送请求, 提交设置, 在请求的回调函数中, 判断用户是否登录, 如未登录则跳转到登录页面, 否则根据成功的状态码将页面跳转到个人中心(这是我个人主张的做法)

----

####  2. 后端部分

API视图函数介绍:

| Views                                  | Description      |
| -------------------------------------- | ---------------- |
| ihome.api_1_0.user.views.get_real_name | 获取用户实名信息 |
| ihome.api_1_0.user.views.set_real_name | 设置用户实名信息 |

**接口一get_real_name:**

1. 验证用户登录状态
2. 从g对象中获取user_id
3. 根据user_id查询到用户用户对象
4. 调用模型中(user对象)封装好的user.auth_to_dict()方法, 将用户个人基本信息转为字典对象
5. 向客户端返回状态码及个人信息字典对象

**接口二set_real_name:**

1. 验证用户登录状态
2. 获取参数(用户真实姓名和身份证号码)
3. 效验参数完整性
4. 效验身份证格式是否合法
5. 将用户实名信息添加到user表中, 但设置的条件必须是该用户的id, 且真实姓名和身份证号都是为None的情况下, 才允许设置(这确保用户是第一次设置)
6. 设置成功后返回状态码及状态信息给客户端

----



## 我的房源-作为房东可发布
#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | myhouse.html |
| /ihome/static/js   | myhouse.js |

1. 该页面以展示发布的房源信息为主, 除了点击房屋图片跳转到房屋详情页之外, 几乎没有其它操作
2. 页面初始化, 先向服务端发送请求, 获取用户的实名认证状态, 根据返回的状态码判断用户是否通过实名认证
3. 如果返回的用户实名信息为空, 说明用户未经过实名认证, 此时用户不可发布新房源, 而是向用户展示去实名认证的提示按钮
4. 如果用户已经过实名验证, 则继续发送一次请求, 获取用户名下已发布的所有房屋信息列表, 并将其展示在页面中
5. 这里需要注意一点, 所展示的每个房屋信息都有一个超链接, 点击会跳转到该房屋对应的房屋详情页面, 所以我们应该在脚本中, 设置好跳转的URL地址, 但房屋id的参数要预留出来, 在页面中动态的追加上, 从而可以跳转到每个房屋对应的详情页面中

----

####  2. 后端部分

API视图函数介绍:

| Views                                    | Description            |
| ---------------------------------------- | ---------------------- |
| ihome.api_1_0.user.views.get_real_name   | 获取用户实名认证信息   |
| ihome.api_1_0.house.views.get_user_house | 获取用户发布的房源信息 |

**接口一get_real_name:**

1. 验证用户登录状态
2. 从g对象中获取用户id, 根据该id查询user表, 获取用户对象
3. 返回状态码及状态信息, 和用户数据(调用模型中自封装的auth_to_dict()方法, 将用户信息转为字典对象), 将其返回给客户端

**接口二get_user_house:**

1. 验证用户登录状态
2. 获取用户id(从g对象中)
3. 获取user对象, 根据该对象中在house表中映射的查询属性, 获取所有与该用户关联的房屋对象
4. 遍历所有的房屋对象, 调用在该对象中封装的to_basic_dict()方法(将每个房屋信息转为字典), 得到每个房屋信息的字典对象, 将其添加一个列表中
5. 返回状态码及状态信息, 和前面包含所有房屋信息的列表到客户端

----



## 发布新房源-房源信息提交页

#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | myhouse.html |
| /ihome/static/js   | myhouse.js |

####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
|||
||



----



# 搜索列表页

![](http://image.weidong168.com/ihome_search.jpg)



#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | search.html |
| /ihome/static/js   | search.js |



####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
|||
||



----



# 房屋详情页

![](http://image.weidong168.com/ihome_details.png)



#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | detail.html |
| /ihome/static/js   | detail.js |



####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
|||
||



----



# 房屋预定-订单创建页

![](http://image.weidong168.com/ihome_oreder_create.jpg)



#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | booking.html |
| /ihome/static/js   | booking.js |



####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
|||
||



----



# 我的订单-基于客户

![](http://image.weidong168.com/ihome_my_order.jpg)



#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | orders.html |
| /ihome/static/js   | orders.js |



####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
|||
||



----



# 客户订单-基于房东

![](http://image.weidong168.com/ihome_client_order.jpg)



#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | lorders.html |
| /ihome/static/js   | lorders.js |



####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
|||
||



----



# 订单支付及评论

![](http://image.weidong168.com/ihome_alipay.jpg)



#### 1. 前端部分

主要文件:

| Path               | File       |
| ------------------ | ---------- |
| /ihome/static/html | orders.html |
| /ihome/static/js   | orders.js |



####  2. 后端部分

API视图函数介绍:

| Views                                     | Description                                          |
|||
||



----



# 其它说明







