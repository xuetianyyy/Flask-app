from . import api_order
from flask import g, current_app, jsonify
from utils.commons import login_required
from api_1_0.order.models import Order
from utils.response_code import RET
from ihome import db
from alipay import AliPay
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# POST /api/1.0/order/<int:order_id>/pay
@api_order.route('/<int:order_id>/pay', methods=['POST'])
@login_required
def order_pay(order_id):
    """ 订单支付接口
    Args:
        order_id: 订单编号
    """
    user_id = g.user_id
    # 判断订单状态, 订单必须是待支付状态
    try:
        order = Order.query.filter(Order.id == order_id, user_id == user_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    else:
        if order is None:
            return jsonify(errcode=RET.NODATA, errmsg="您交易的订单不存在")

    # 业务处理: 使用python sdk调用支付宝的支付接口
    app_private_key_path = os.path.join(BASE_DIR, 'order/app_private_key.pem')
    alipay_public_key_path = os.path.join(BASE_DIR, 'order/alipay_public_key.pem')

    # 接口初始化
    alipay = AliPay(
        appid="2016092600598274",                     # 必选, 这个在沙箱或应用中即可看到
        app_notify_url=None,                          # 可选, 默认回调url
        app_private_key_path=app_private_key_path,    # 必选, 指定本地的公钥, 前面有两种方式定义这个变量
        # 必选, 指定支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=alipay_public_key_path,
        # 可选, RSA 或者 RSA2(支付宝推荐)
        sign_type="RSA2",
        # 可选, 默认False(代表实际项目环境), 如果是支付宝沙箱环境需要改为True
        debug=True,
    )

    # 调用支付接口, 手机网站支付: alipay.trade.wap.pay
    # 手机网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    # 如果是沙箱, 需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    order_trade = '86308596' + str(order_id)
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order_trade,  # 订单编号
        total_amount=str(order.amount / 100.0),   # 订单金额
        subject='测试订单-{}'.format(order_trade),  # 订单标题, 如果是python2需要转为utf-8编码
        # return_url='http://192.168.137.1:5000/orders.html',
        return_url=None,    # 同步回调访问地址, 支付宝的结果返回页面, 如若没有就写None
        # 异步回调访问地址, 支付宝的结果默认以这个为准, 可选, 不填则使用默认notify url
        notify_url=None,
    )

    # 返回应答, 返回支付链接, 网关链接在配置文件中获取
    alipay_url = current_app.config.get('ALIPAY_URL') + '?' + order_string
    return jsonify(errcode=RET.OK, errmsg="OK", pay_url=alipay_url)


# GET /api/1.0/order/<int:order_id>/pay-query
@api_order.route('/<int:order_id>/pay-query')
@login_required
def pay_query(order_id):
    """ 订单支付状态查询
    Args:
        order_id: 订单编号
    """
    user_id = g.user_id
    # 判断订单状态, 订单必须是待支付状态
    try:
        order = Order.query.filter(Order.id == order_id, user_id == user_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errcode=RET.DBERR, errmsg="数据库异常")
    else:
        if order is None:
            return jsonify(errcode=RET.NODATA, errmsg="您交易的订单不存在")

    # 3. 查询支付: 调用接口
    # 接口初始化
    alipay = AliPay(
        appid="2016092600598274",
        app_notify_url=None,
        app_private_key_path=os.path.join(BASE_DIR, 'order/app_private_key.pem'),
        alipay_public_key_path=os.path.join(BASE_DIR, 'order/alipay_public_key.pem'),
        sign_type="RSA2",
        debug=True,
    )
    order_trade = '86308596' + str(order_id)    # 订单编号

    # 调用订单查询接口
    while True:
        # 这个接口是订单查询的api
        response = alipay.api_alipay_trade_query(order_trade)
        # 这是返回的数据形式, 在支付宝开发文档中也可以看到
        # response = {
        #     "trade_no": "2017032121001004070200176844",  # 支付宝交易号
        #     "code": "10000",  # 接口调用是否成功
        #     "invoice_amount": "20.00",
        #     "open_id": "20880072506750308812798160715407",
        #     "fund_bill_list": [
        #             {
        #                 "amount": "20.00",
        #                 "fund_channel": "ALIPAYACCOUNT"
        #             }
        #     ],
        #     "buyer_logon_id": "csq***@sandbox.com",
        #     "send_pay_date": "2017-03-21 13:29:17",
        #     "receipt_amount": "20.00",
        #     "out_trade_no": "out_trade_no15",
        #     "buyer_pay_amount": "20.00",
        #     "buyer_user_id": "2088102169481075",
        #     "msg": "Success",
        #     "point_amount": "0.00",
        #     "trade_status": "TRADE_SUCCESS",  # 支付结果
        #     "total_amount": "20.00"
        # }
        code = response.get('code')  # 支付宝的接口调用状态码
        if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
            # 支付成功
            # 获取支付宝交易单号
            trade_no = response.get('trade_no')
            # 更新订单状态
            order.trade_no = trade_no   # 支付单号
            order.status = "WAIT_COMMENT"       # 支付状态待评价

            try:
                db.session.add(order)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errcode=RET.DBERR, errmsg="数据库异常, 订单更新失败")

            # 返回结果
            return jsonify(errcode=RET.OK, errmsg="交易成功")
        elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
            # 等待买家付款
            # 业务处理失败，可能一会就会成功
            import time
            time.sleep(5)
            continue
        else:
            # 支付出错
            return jsonify(errcode=RET.THIRDERR, errmsg="您交易的订单不存在")
