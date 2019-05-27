from . import api_order
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


# GET /api/1.0/order/house?house_id=xxx
@api_order.route('/house')
@login_required
def get_order_hosue():
    """ 页面初始化需要获取的订单房屋信息 """
    # 接收效验参数
    house_id = request.args.get('house_id')

    if house_id is None:
        return jsonify(errcode=RET.PARAMERR, errmsg="缺少参数")

    order_status = "WAIT_ACCEPT"
    try:
        house = House.query.filter_by(id=house_id).first()
        if house.orders:
            order_status = house.orders[0].status  # 订单状态
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    return jsonify(errcode=RET.OK, errmsg="OK", data=house.to_basic_dict(), order_status=order_status)


# POST /api/1.0/order/orders
@api_order.route('/orders', methods=['POST'])
@login_required
def sava_order():
    """ 保存用户订单

    Request Body Params:
        json数据, 如下:
        {
            house_id:   房屋id
            start_date: 起始入住时间
            end_date:   结束入住时间
        }

    """
    user_id = g.user_id

    # 获取参数
    order_data = request.get_json()
    if not order_data:
        return jsonify(errcode=RET.PARAMERR, errmsg="没有提交信息")

    house_id = order_data.get('house_id')           # 预定的房屋编号
    start_date_str = order_data.get('start_date')   # 预定的起始日期
    end_date_str = order_data.get('end_date')       # 结束入住的日期

    # 参数效验
    if not all([house_id, start_date_str, end_date_str]):
        return jsonify(errcode=RET.PARAMERR, errmsg="缺少参数")

    # 日期格式检查
    try:
        # 将请求的时间参数字符串转换为datetime类型
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        assert start_date <= end_date
        # 计算预定的天数
        days = (end_date - start_date).days + 1
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.PARAMERR, errmsg="日期格式错误")

    # 查询房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="获取房屋数据失败")
    else:
        if house is None:
            return jsonify(errcode=RET.NODATA, errmsg="您要查询的房屋数据不存在")

    # 判断预定的房屋是不是房东自己的(防止房东自己刷单)
    if user_id == house.user_id:
        return jsonify(errcode=RET.ROLEERR, errmsg="房东不能预定自己的房屋")

    # 确保用户预定的时间内, 房屋没有被人下单
    try:
        # 查询时间冲突的订单, 只有待接单, 待支付, 已支付, 或待评价三个状态的单, 说明在预定或消费期间中
        count = Order.query.filter(Order.house_id == house_id, Order.begin_date <= end_date, Order.end_date >= start_date, Order.status.in_(["WAIT_ACCEPT", "WAIT_PAYMENT", "PAID", "WAIT_COMMENT"])).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="检查出错, 请稍后重试")
    else:
        if count > 0:
            return jsonify(errcode=RET.DATAERR, errmsg="非常抱歉, 房屋已被预定")

    # 订单总额
    amount = days * house.price

    # 保存订单数据
    order = Order(house_id=house_id,
                  user_id=user_id,
                  begin_date=start_date,
                  end_date=end_date,
                  days=days,
                  house_price=house.price,
                  amount=amount,)
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errcode=RET.DBERR, errmsg="保存订单失败")

    return jsonify(errcode=RET.OK, errmsg="OK", data={'order_id': order.id})


# GET /api/1.0/order/orders?role=customer  或  role=landlord
@api_order.route('/orders')
@login_required
def get_user_orders():
    """ 查询用户的订单信息

    Url Params:
        role:  用户身份信息(customer顾客)或(landlord房东)

    """
    user_id = g.user_id

    # 用户的身份, 用户想要查询作为房客预定其它房东的订单, 还是想作为房东预定查询别人预定自己的订单
    role = request.args.get('role', '')

    # 查询订单数据
    try:
        if role == 'landlord':
            # 以房东的身份查询订单, 查询自己名下的房子, 有哪些预定
            # 先查询自定名下有哪些房子
            houses = House.query.filter(House.user_id == user_id).all()
            houses_ids = [house.id for house in houses]
            # 再查询自己的房子, 有哪些顾客预定的订单
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).order_by(Order.create_time.desc()).all()
        else:
            # 以顾客的身份查询自己预定过哪些订单
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="查询订单信息失败")

    # 将订单对象转换为字典数据
    orders_dict_list = []
    if orders:
        for order in orders:
            # order.to_dict()是在模型中封装的方法, 返回查询信息的字典
            orders_dict_list.append(order.to_dict())

    return jsonify(errcode=RET.OK, errmsg="OK", data={'orders': orders_dict_list})


# PUT /api/1.0/order/<int:order_id>/status
@api_order.route('/<int:order_id>/status', methods=['PUT'])
@login_required
def accept_reject_order(order_id):
    """ 房东接单 拒单操作

    Args:
        order_id: 订单id

    Request Body Params:
        json数据, 如下:
            { "action": "accept" | "reject" }

        如果action == "reject", 那么还要携带拒单原因的参数, 如下:
        {"action": "reject", "reason": "拒单原因"}

    """
    user_id = g.user_id

    # 获取参数
    req_data = request.get_json()
    if not req_data:
        return jsonify(errcode=RET.PARAMERR, errmsg='您没有提交信息')

    # action参数表明客户端请求的是接单还是拒单的行为
    action = req_data.get('action')

    if action not in ['accept', 'reject']:
        # 如果参数不是这两个中的其中一个
        return jsonify(errcode=RET.PARAMERR, errmsg="参数错误")

    try:
        # 根据订单号查询订单, 并且要求订单处于等待接单的状态
        order = Order.query.filter(Order.id == order_id, Order.status == 'WAIT_ACCEPT').first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.REQERR, errmsg="无法获取订单数据")

    # 确保房东只能修改属于自己房子的订单
    if not order or house.user_id != user_id:
        return jsonify(errcode=RET.REQERR, errmsg="非法的操作")

    if action == 'accept':
        # 接单, 将订单状态设置为等待支付
        order.status = "WAIT_PAYMENT"
    elif action == 'reject':
        # 拒单, 要求房东传递拒单原因
        reason = req_data.get('reason')
        if not reason:
            return jsonify(errcode=RET.PARAMERR, errmsg="参数错误")
        order.status = 'REJECTED'
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常, 提交失败")

    return jsonify(errcode=RET.OK, errmsg="OK")


# POST /api/1.0/order/<int:order_id>/comment
@api_order.route('/<int:order_id>/comment', methods=["PUT"])
@login_required
def sava_order_comment(order_id):
    """ 保存订单评论信息

    Request Body Params:
        {"comment": "评论信息"}

    """
    user_id = g.user_id
    # 获取参数
    req_data = request.get_json()
    comment = req_data.get('comment')

    # 检查参数
    if not comment:
        return jsonify(errcode=RET.PARAMERR, errmsg="您没有提交信息")

    try:
        # 需要确保只能评论自己下的订单, 而且处于待评价状态才可以
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == 'WAIT_COMMENT').first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg='无法获取订单数据')
    else:
        if order is None:
            return jsonify(errcode=RET.DBERR, errmsg="操作无效")

    try:
        # 将订单的状态设置为已完成
        order.status = 'COMPLETE'
        # 保存订单的评价信息
        order.comment = comment
        # 将房屋的完成订单数量增加1
        house.order_count += 1
        db.session.add(order)
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errcode=RET.DBERR, errmsg='数据库异常, 提交失败')

    # 因为房屋详情中有订单的评价信息, 为了让最新的评价信息展示在房屋详情中, 所以删除reidis中关于本订单的的房屋信息
    try:
        redis_conn.delete('house_info_{}'.format(order.house_id))
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errcode=RET.OK, errmsg='OK')
