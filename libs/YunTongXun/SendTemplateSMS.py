from .CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在控制台首页中看到开发者主账号ACCOUNT SID。
accountSid = '开发者主账号ACCOUNT SID'

# 说明：主账号Token，登陆云通讯网站后，可在控制台首页中看到开发者主账号AUTH TOKEN
accountToken = '开发者主账号AUTH TOKEN'

# 请使用管理控制台中已创建应用的APPID, 注意: 测试环境只能使用未上线的应用
appId = '应用的APPID'

# 说明：请求地址，生产环境配置成app.cloopen.com
serverIP = 'app.cloopen.com'

# 说明：请求端口 ，生产环境为8883
serverPort = '8883'

# 说明：REST API版本号保持不变
softVersion = '2013-12-26'


class CCP:
    """ 自己封装的发送短信辅助类 """

    # 用来记录第一个被实例化的引用
    instance = None

    def __new__(cls):
        # 判断是否存在实例的引用
        if cls.instance is None:
            # 如果不存在, 则引用父类为该实例分配空间(引用)
            obj = super().__new__(cls)

            # 初始化REST SDK, 这里的obj就相当于当前实例对象的self, 这可以保证它只被初始化一次
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls.instance = obj

        # 如果存在实例, 则返回该实例的固定引用
        return cls.instance

    def sendTemplateSMS(self, to, datas, tempId):
        """ 发送短信的方法

        Args:
            to:     str 接收者的手机号, 也可以是多个, 如: "131..., 132..., ..."
            datas:  list 或 '' 发送的内容数据列表(内容需为字符串)
                    如: ['验证码', '失效分钟'] 如没有内容请填写''
            tempId: str 模板Id (免费测试的模板Id为1)
        Returns:
            成功: 0
            失败: -1

        """
        result = self.rest.sendTemplateSMS(to, datas, tempId)

        # 打印响应信息
        # for k, v in result.items():

        #     if k == 'templateSMS':
        #         for k, s in v.items():
        #             print('{}:{}'.format(k, s))
        #     else:
        #         print('{}:{}'.format(k, v))

        # 获取响应码
        status_code = result.get('statusCode')
        if status_code == '000000':
            # 表示发送成功
            return 0
        else:
            # 发送失败
            return -1

if __name__ == '__main__':
    ccp = CCP()
    ccp.sendTemplateSMS('18664685380', ['12345', '2'], '1')
