from ihome.models import BaseModel
from ihome import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(BaseModel, db.Model):
    """用户"""

    __tablename__ = "ih_user_profile"

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户暱称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    real_name = db.Column(db.String(32))  # 真实姓名
    id_card = db.Column(db.String(20), unique=True)  # 身份证号
    avatar_url = db.Column(db.String(128))  # 用户头像路径
    houses = db.relationship("House", backref="user")  # 用户发布的房屋
    orders = db.relationship("Order", backref="user")  # 用户下的订单

    # 加上property装饰器后，会把函数变为属性，属性名即为函数名,
    # 注意: 这里它仅是作为这个类的属性, 而不是数据库的字段属性, 因为它不是使用db设置的属性值
    @property
    def password(self):
        """ 读取属性的函数行为

        读取属性时将被调用, 例如: print(user.password)
        函数的返回值会作为属性值, 注意: 使用property必须要有返回值
        return "xxxx"

        """
        raise AttributeError("这个属性只能设置，不能读取")

    # 使用这个装饰器, 可以对@property构建的属性, 进行属性设置的相关操作
    @password.setter
    def password(self, password):
        """ 它在设置属性时被调用

        设置属性的方式:  user.passord = "xxxxx"
        :param password: 该参数就是设置属性时的属性值, 如上面的"xxxxx", (这是原始的明文密码)
        :return:

        """
        # 在视图中设置user.password属性值时, 该方法被调用, 就会接收到password参数, 并将其设置为字段值
        self.password_hash = generate_password_hash(password)

    def check_password(self, passwd):
        """ 检验密码的正确性

        :param passwd:  用户登录时填写的原始密码
        :return: 如果正确，返回True， 否则返回False

        """
        return check_password_hash(self.password_hash, passwd)

    def to_dict(self):
        """ 将对象转换为字典数据 """
        user_dict = {
            "user_id": self.id,
            "username": self.name if self.name else "未设置",
            "mobile": self.mobile,
            "image_url": self.avatar_url if self.avatar_url else "",
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict

    def auth_to_dict(self):
        """ 将实名信息转换为字典数据 """
        auth_dict = {
            "user_id": self.id,
            "real_name": self.real_name if self.real_name else '',
            "id_card": self.id_card if self.id_card else ''
        }
        return auth_dict
