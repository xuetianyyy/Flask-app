from . import api_house
from flask import request, jsonify, session, current_app, g, session
from utils.response_code import RET
from ihome import redis_conn, db
from api_1_0.user.models import User
from api_1_0.order.models import Order
from api_1_0.house.models import Area, House, Facility, HouseImage
from sqlalchemy.exc import IntegrityError
import re
import json
from datetime import datetime
# 自定义的登录装饰器
from utils.commons import login_required
# 七牛云上传图片
from utils.image_storage import storage


# GET /api/1.0/house/index
@api_house.route('/index')
def get_house_index():
    """ 获取主页幻灯片 """
    # 设置首页获取首页的幻灯片数量
    HOME_PAGE_MAX_IMAGE = 5
    # 尝试从缓存中读取
    try:
        json_houses = redis_conn.get('home_page_data')
    except Exception as e:
        current_app.logger.error(e)

    if json_houses is not None:
        return '{{"errcode": "0", "errmsg": "OK", "data": {}}}'.format(json_houses.decode()), 200, {"Content-Type": "application/json"}
    else:
        # 查询数据库
        try:
            houses = House.query.order_by(House.order_count.desc()).limit(HOME_PAGE_MAX_IMAGE).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode=RET.DBERR, errmsg="查询数据库失败")

        if not houses:
            return jsonify(errcode=RET.NODATA, errmsg="抱歉, 暂时没有查到数据")

        houses_list = []
        # 遍历house表的查询集
        for house in houses:
            # 如果房屋未设置主图片, 则跳过
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())

        # 将数据转换为json, 并保存到redis缓存中, 字符串类型
        json_houses = json.dumps(houses_list)
        # 获取redis缓存时间
        home_page_data_redis_expires = current_app.config.get('HOME_PAGE_DATA_REDIS_EXPIRES')
        try:
            redis_conn.set('home_page_data', json_houses, ex=home_page_data_redis_expires)
        except Exception as e:
            current_app.logger.error(e)

        return '{{"errcode": "0", "errmsg": "OK", "data": {}}}'.format(json_houses), 200, {"Content-Type": "application/json"}


# GET /api/1.0/house/details?house_id=xxx
@api_house.route('/details')
def get_hosue_details():
    """ 获取房屋详情信息　"""
    # 接收路径参数
    house_id = request.args.get('house_id')
    if not house_id:
        return jsonify(errcode=RET.PARAMERR, errmsg="缺少必须参数, 请检查路径是否正确")

    # 尝试获取访问者的id, 如果获取为空, 将使用默认值'-1'替代
    call_user_id = session.get('user_id', '-1')

    # 尝试从redis中读取缓存数据
    try:
        json_house = redis_conn.get('house_info_{}'.format(house_id))
    except Exception as e:
        current_app.logger.error(e)
    else:
        if json_house is not None:
            return '{{"errcode": "0", "errmsg": "OK", "data": {0}, "call_user_id": {1}}}'.format(json_house.decode(), call_user_id), \
                200, {"Content-Type": "application/json"}

    # 查询数据库
    try:
        house = House.query.filter_by(id=house_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

    if house is None:
        return jsonify(errcode=RET.NODATA, errmsg="没有查询到数据")

    try:
        # 先将数据转换为字典, 这是在模型中封装的方法
        house_data_dict = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.SERVERERR, errmsg="数据提取失败, 请联系管理员")
    else:
        # 将数据存放到redis中
        json_house = json.dumps(house_data_dict)

    # 获取设置的redis过期时间, 配置文件中
    redis_expires = current_app.config.get('HOME_PAGE_DATA_REDIS_EXPIRES')
    try:
        redis_conn.set('house_info_{}'.format(house_id), json_house, ex=redis_expires)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="设置缓存异常")

    # return jsonify(errcode=RET.OK, errmsg="OK", data=house.to_full_dict())
    return '{{"errcode": "0", "errmsg": "OK", "data": {0},  "call_user_id": {1}}}'.format(
        json_house, call_user_id), 200, {"Content-Type": "application/json"}


# GET /api/1.0/house/house-list?sd=2019-05-20&ed=2019-05-30&aid=10&sk=new&p=1
@api_house.route('/house-list')
def get_house_list():
    """ 获取房屋的列表信息 (搜索页面)

    Url Params:
        sd:  用户搜索的起始入住时间
        ed:  用户搜索的结束入住时间
        aid: 区域编号(id)
        sk:  排序方式
        p:   页码

    """
    # 获取参数
    start_date = request.args.get('sd')
    end_date = request.args.get('ed')
    area_id = request.args.get('aid')
    sort_key = request.args.get('sk', 'new')  # 如果没有则使用默认值
    page = request.args.get('p')

    # 处理时间
    try:
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if all([start_date, end_date]):
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.PARAMERR, errmsg="非法的日期时间参数")

    # 判断区域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode=RET.PARAMERR, errmsg="您选择的区域不在业务范围中")

    # 处理页码
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        # 如果数据非法, 则设置为第一页
        page = 1

    # 设置redis的hash键名
    redis_hkey = 'house_{0}_{1}_{2}_{3}'.format(start_date, end_date, area_id, sort_key)
    # 尝试从redis中读取缓存
    try:
        resp_json = redis_conn.hget(redis_hkey, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            return resp_json.decode(), 200, {"Content-Type": "application/json"}

    # 时间条件
    # 过滤条件的参数列表容器
    filter_params = []

    # 填充过滤参数
    conflict_orders = None

    # 先查询时间冲突的订单
    try:
        if all([start_date, end_date]):
            conflict_orders = Order.query.filter(Order.begin_date <= end_date, Order.end_date >= start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库查询异常")

    if conflict_orders:
        # 从订单中获取重读的房屋id
        conflict_house_ids = [order.house_id for order in conflict_orders]
        # 只有当订单冲突的房屋id列表不为空, 才对整个房屋数据进行not in conflict_house_ids查询, 并将记录添加到容器中
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))

    # 区域条件
    if area_id:
        # 它类似于apend(House.query.filter_by(area_id=area_id)), 这里的House.area_id == area_id返回的是一个查询表达式
        filter_params.append(House.area_id == area_id)

    # 查询数据库, 补充排序条件
    if sort_key == 'booking':
        # 入住最多
        house_qury = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == 'price-inc':
        # 价格由低到高
        house_qury = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == 'price-des':
        house_qury = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        # 更新时间, 也是默认值
        house_qury = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 获取每页展示的查询记录数量, 在配置中
    per_page = current_app.config.get('HOUSE_LIST_PER_PAGE')
    # 处理分页
    try:
        page_obj = house_qury.paginate(page=page, per_page=per_page, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库查询异常")

    # 获取页面数据
    house_li = page_obj.items
    # 得到所有房屋信息的字典对象
    houses = [house.to_basic_dict() for house in house_li]
    # 获取总页数
    total_page = page_obj.pages
    # 是否有下一页
    has_next = page_obj.has_next

    # 将返回数据, 转为json字符串
    resp_json = json.dumps(dict(errcode=RET.OK, errmsg="OK", data={"total_page": total_page, "houses": houses, "page": page, 'has_next': has_next}))
    # 获取搜索列表的缓存过期时间, 在配置中
    house_search_list_expires = current_app.config.get('HOUSE_SEARCH_LIST_EXPIRES')

    # 设置redis缓存hash数据, key为house_{start_date}_{end_date}_{area_id}_{sort_key}, value_key为页码
    if page <= total_page:
        try:
            # 页码必须小于总页数, 才设置缓存
            pipeline = redis_conn.pipeline()
            pipeline.multi()
            pipeline.hset(redis_hkey, page, resp_json)
            pipeline.expire(redis_hkey, house_search_list_expires)
            pipeline.execute()  # 提交保存
        except Exception as e:
            current_app.logger.error(e)

    return resp_json, 200, {"Content-Type": "application/json"}


# GET /api/1.0/house/get-area-info
@api_house.route('/get-area-info')
def get_area_info():
    """ 获取城区信息 """
    # 尝试从redis中读取数据, 如果读取成功则使用缓存返回给前端, 否则从数据库获取
    try:
        resp_json = redis_conn.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            # 代表redis中已经具有缓存数据
            current_app.logger.info('hit redis area_info')  # 表示拿到了数据, 记录日志
            return resp_json, 200, {'Content-Type': 'application/json'}

    # 查询数据库读取城区信息
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

    area_dict_li = []
    # 将对象转为字典
    for area in area_li:
        # 得到每行数据的字段, to_dict是在model里封装的方法
        area_dict_li.append(area.to_dict())

    # 将返回的数据转换为json字符串
    resp_dict = dict(errcode=RET.OK, errmsg='ok', data=area_dict_li)
    resp_json = json.dumps(resp_dict)

    # 将数据保存到redis中
    try:
        # 注意这里一定要设置有效期, 否则哪怕数据库的记录更新了, 返回给前端的也是历史记录的缓存
        redis_conn.set('area_info', resp_json, ex=current_app.config.get('AREA_INFO_REDIS_CACHE_EXPIRES'))
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {'Content-Type': 'application/json'}


# POST /api/1.0/house/save-houses-info
@api_house.route('/save-houses-info', methods=['POST'])
@login_required
def save_house_info():
    """ 保存房屋基本信息

    Request Body Params:
        该参数需要包含在一个json类型的字典中
        title: 房屋标题
        price: 租住价格
        area_id: 所在城区id, 如: '1'
        address: 房屋地址
        room_count: 房间数量
        acreage: 房间面积
        unit: 户型描述, 如: 三室两厅两卫...
        capacity: 可入住人数
        beds: 卧床配置, 如: 大床1.8 * 2m
        deposit: 押金金额
        min_days: 入住最少天数
        max_days: 入住最多天数
        facilitys: 设置id列表, 如: ['7', '8', ...]

    Returns:
        对象的状态码, 和响应信息

    """
    house_dict = request.get_json()
    user_id = g.user_id
    title = house_dict.get("title")
    price = house_dict.get("price")
    area_id = house_dict.get("area_id")
    address = house_dict.get("address")
    room_count = house_dict.get("room_count")
    acreage = house_dict.get("acreage")
    unit = house_dict.get("unit")
    capacity = house_dict.get("capacity")
    beds = house_dict.get("beds")
    deposit = house_dict.get("deposit")
    min_days = house_dict.get("min_days")
    max_days = house_dict.get("max_days")

    # 效验参数完整性
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(error=RET.PARAMERR, errmsg='参数不全')

    # 判断租房金额和押金金额是否可以转为int类型
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.PARAMERR, errmsg="参数错误")

    # 判断城区id是否存在
    try:
        area = Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据异常")
    else:
        # 如果数据库没有该条记录
        if area is None:
            return jsonify(error=RET.NODATA, errmsg="城区信息有误")

    # 保存房屋信息, 到数据库中
    house = House(user_id=user_id,
                  title=title,
                  price=price,
                  area_id=area_id,
                  address=address,
                  room_count=room_count,
                  acreage=acreage,
                  unit=unit,
                  capacity=capacity,
                  beds=beds,
                  deposit=deposit,
                  min_days=min_days,
                  max_days=max_days,
                  )

    # 数据库保存操作
    try:
        db.session.add(house)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="保存数据异常")

    # 处理房屋的设施信息
    facility_ids = house_dict.get("facility")

    # 如果用户勾选了设施信息, 再保存数据库
    if facility_ids:
        try:
            # 过滤列表中的id, 取到对应的行, 如果是预期之外的id, 将返回None, 它返回每一行的查询集列表
            facilitys = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errcode=RET.DBERR, errmsg="数据库异常")

        if facilitys:
            # 表示有合法的设施数据, 则需要保存它们
            house.facilities = facilitys

    # 进行最终的保存和回滚
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errcode=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errcode=RET.OK, errmsg="数据提交成功", data={'house_id': house.id})


# POST /api/1.0/house/image
@api_house.route('/image', methods=['POST'])
@login_required
def save_house_image():
    """ 保存房屋的图片

    Request Body Params:
        image_file: 图片
        house_id: 房屋id

    Returns:
        对象的状态码, 和响应信息

    """
    image_file = request.files.get('image_file')
    # 多媒体表单中是可以携带字符串参数的, 所以我们可以在表单中同时获取到它
    house_id = request.form.get('house_id')

    # 参数效验
    if not all([image_file, house_id]):
        return jsonify(errcode=RET.PARAMERR, errmsg="参数错误")

    # 判断房屋id的正确性
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    else:
        if house is None:
            return jsonify(errcode=RET.NODATA, errmsg="房屋不存在")

    # 保存图片到七牛中
    image_data = image_file.read()
    try:
        image_url = storage(current_app.config.get('QINIU_ZONE_HOST'), image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.THIRDERR, errmsg='保存图片失败')

    # 保存图片信息到数据库中
    house_image = HouseImage(house_id=house_id, url=image_url)
    db.session.add(house_image)

    # 保存作为主页的房屋图片, 只设置一张, 先判断它是否已经设置过, 否则不设置
    if not house.index_image_url:
        house.index_image_url = image_url
        db.session.add(house)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errcode=RET.DBERR, errmsg="主页图片保存失败")

    return jsonify(errcode=RET.OK, errmsg='ok', data={'image_url': image_url})


# GET /api/1.0/house/user-house
@api_house.route('/user-house')
@login_required
def get_user_house():
    """ 获取用户房屋信息 """
    user_id = g.user_id

    # 查询数据库
    try:
        user = User.query.get(user_id)
        houses = user.houses  # 得到用户发布的房屋表
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="获取数据失败")

    # 将查询到的房屋信息转为字典存到的列表中
    houses_list = []
    if houses:
        for house in houses:
            # 将每个房屋信息的字典, 添加到列表中, to_basic_dict()是在House的模型中封装的方法
            houses_list.append(house.to_basic_dict())

    return jsonify(errcode=RET.OK, errmsg="OK", data={"houses": houses_list})
