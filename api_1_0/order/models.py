from ihome.models import BaseModel
from ihome import db


class Order(BaseModel, db.Model):
    """订单"""

    __tablename__ = "ih_order_info"

    id = db.Column(db.Integer, primary_key=True)  # 订单编号
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False)  # 下订单的用户编号
    house_id = db.Column(db.Integer, db.ForeignKey("ih_house_info.id"), nullable=False)  # 预订的房间编号
    begin_date = db.Column(db.DateTime, nullable=False)  # 预订的起始时间
    end_date = db.Column(db.DateTime, nullable=False)    # 预订的结束时间
    days = db.Column(db.Integer, nullable=False)         # 预订的总天数
    house_price = db.Column(db.Integer, nullable=False)  # 房屋的单价
    amount = db.Column(db.Integer, nullable=False)       # 订单的总金额
    status = db.Column(  # 订单的状态
        db.Enum(   # 枚举        # django choice
            "WAIT_ACCEPT",      # 待接单,
            "WAIT_PAYMENT",     # 待支付
            "PAID",             # 已支付
            "WAIT_COMMENT",     # 待评价
            "COMPLETE",         # 已完成
            "CANCELED",         # 已取消
            "REJECTED"          # 已拒单
        ),
        default="WAIT_ACCEPT", index=True)      # 指明在mysql中这个字段建立索引，加快查询速度
    comment = db.Column(db.Text)                # 订单的评论信息或者拒单原因
    trade_no = db.Column(db.String(80))         # 交易的流水号 支付宝的

    def to_dict(self):
        """将订单信息转换为字典数据"""
        order_dict = {
            "order_id": self.id,
            "title": self.house.title,
            "img_url": self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""
        }
        return order_dict
