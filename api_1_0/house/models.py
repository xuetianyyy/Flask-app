from ihome.models import BaseModel
from ihome import db
from api_1_0.order.models import Order
from flask import current_app


class Area(BaseModel, db.Model):
    """城区"""

    __tablename__ = "ih_area_info"

    id = db.Column(db.Integer, primary_key=True)  # 区域编号
    name = db.Column(db.String(32), nullable=False)  # 区域名字
    houses = db.relationship("House", backref="area")  # 区域的房屋

    def to_dict(self):
        """将对象转换为字典"""
        d = {
            "aid": self.id,
            "aname": self.name
        }
        return d


# 房屋设施表，建立房屋与设施的多对多关系, 直接以SQLAlchemy的原始方式创建表
house_facility = db.Table(
    "ih_house_facility",
    db.Column("house_id", db.Integer, db.ForeignKey("ih_house_info.id"), primary_key=True),  # 房屋编号
    db.Column("facility_id", db.Integer, db.ForeignKey("ih_facility_info.id"), primary_key=True)  # 设施编号
)


class House(BaseModel, db.Model):
    """房屋信息"""

    __tablename__ = "ih_house_info"

    id = db.Column(db.Integer, primary_key=True)        # 房屋编号
    user_id = db.Column(db.Integer, db.ForeignKey("ih_user_profile.id"), nullable=False)    # 房屋主人的用户编号
    area_id = db.Column(db.Integer, db.ForeignKey("ih_area_info.id"), nullable=False)       # 归属地的区域编号
    title = db.Column(db.String(64), nullable=False)    # 标题
    price = db.Column(db.Integer, default=0)            # 单价，单位：分
    address = db.Column(db.String(512), default="")     # 地址
    room_count = db.Column(db.Integer, default=1)       # 房间数目
    acreage = db.Column(db.Integer, default=0)          # 房屋面积
    unit = db.Column(db.String(32), default="")         # 房屋单元， 如几室几厅
    capacity = db.Column(db.Integer, default=1)         # 房屋容纳的人数
    beds = db.Column(db.String(64), default="")         # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)          # 房屋押金
    min_days = db.Column(db.Integer, default=1)         # 最少入住天数
    max_days = db.Column(db.Integer, default=0)         # 最多入住天数，0表示不限制
    order_count = db.Column(db.Integer, default=0)      # 预订完成的该房屋的订单数
    index_image_url = db.Column(db.String(256), default="")             # 房屋主图片的路径
    facilities = db.relationship("Facility", secondary=house_facility)  # 房屋的设施
    images = db.relationship("HouseImage")                              # 房屋的图片
    orders = db.relationship("Order", backref="house")                  # 房屋的订单

    def to_basic_dict(self):
        """将基本信息转换为字典数据"""
        house_dict = {
            "house_id": self.id,
            "title": self.title,
            "price": self.price,
            "area_name": self.area.name,
            "img_url": self.index_image_url if self.index_image_url else "",
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": self.user.avatar_url if self.user.avatar_url else "",
            "ctime": self.create_time.strftime("%Y-%m-%d")
        }
        return house_dict

    def to_full_dict(self):
        """将详细信息转换为字典数据"""
        house_dict = {
            "hid": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_avatar": self.user.avatar_url if self.user.avatar_url else "",
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "acreage": self.acreage,
            "unit": self.unit,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days,
        }

        # 房屋图片
        img_urls = []
        for image in self.images:
            img_urls.append(image.url)
        house_dict["img_urls"] = img_urls

        # 房屋设施
        facilities = []
        for facility in self.facilities:
            facilities.append(facility.id)
        house_dict["facilities"] = facilities

        # 评论信息
        comments = []
        # 获取显示评论的数量
        house_comment_count = current_app.config.get('HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS')
        orders = Order.query.filter(Order.house_id == self.id, Order.status == "COMPLETE", Order.comment != None)\
            .order_by(Order.update_time.desc()).limit(house_comment_count)
        for order in orders:
            comment = {
                "comment": order.comment,  # 评论的内容
                "user_name": order.user.name if order.user.name != order.user.mobile else "匿名用户",  # 发表评论的用户
                # 评价的时间
                "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            comments.append(comment)
        house_dict["comments"] = comments
        return house_dict


class Facility(BaseModel, db.Model):
    """设施信息"""

    __tablename__ = "ih_facility_info"

    id = db.Column(db.Integer, primary_key=True)  # 设施编号
    name = db.Column(db.String(32), nullable=False)  # 设施名字


class HouseImage(BaseModel, db.Model):
    """房屋图片"""

    __tablename__ = "ih_house_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey(
        "ih_house_info.id"), nullable=False)  # 房屋编号
    url = db.Column(db.String(256), nullable=False)  # 图片的路径
