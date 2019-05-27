import hashlib
import base64
import datetime
import requests
import json
from .xmltojson import xmltojson
from xml.dom import minidom


class REST:

    AccountSid = ''
    AccountToken = ''
    AppId = ''
    SubAccountSid = ''
    SubAccountToken = ''
    ServerIP = ''
    ServerPort = ''
    SoftVersion = ''
    Iflog = False  # 是否打印日志
    Batch = ''  # 时间戳
    BodyType = 'json'  # 包体格式，可填值：json 、xml
    Headers = {}       # 请求头

    def __init__(self, ServerIP, ServerPort, SoftVersion):
        """ 初始化

        :param serverIP:    必选参数  服务器地址
        :param serverPort:  必选参数  服务器端口
        :param softVersion: 必选参数  REST版本号

        """
        self.ServerIP = ServerIP
        self.ServerPort = ServerPort
        self.SoftVersion = SoftVersion

    def setAccount(self, AccountSid, AccountToken):
        """ 设置主帐号

        :param AccountSid:   必选参数  主帐号
        :param AccountToken: 必选参数  主帐号Token

        """
        self.AccountSid = AccountSid
        self.AccountToken = AccountToken

    def setSubAccount(self, SubAccountSid, SubAccountToken):
        """ 设置主帐号

        :param SubAccountSid:   必选参数  子帐号
        :param SubAccountToken: 必选参数  子帐号Token

        """
        self.SubAccountSid = SubAccountSid
        self.SubAccountToken = SubAccountToken

    def setAppId(self, AppId):
        """ 设置应用ID
        :param AppId:  需要设置的应用ID
        """
        self.AppId = AppId

    def log(self, url, body, data):
        print('这是请求的URL：')
        print(url)
        print('这是请求包体:')
        print(body)
        print('这是响应包体:')
        print(data)
        print('********************************')

    def sendTemplateSMS(self, to, datas, tempId):
        """ 发送模板短信

        Args:
            to:     必选参数  短信接收彿手机号码集合,用英文逗号分开
            datas:  可选参数  内容数据
            tempId: 必选参数  模板Id, 测试模板默认为1
        Returns:
            成功: 返回对应格式的成功响应体
            失败: 返回对应格式的失败响应体

            例如: 成功的json的响应体
            {'statusCode' : '000000',
             'templateSMS': {'smsMessageSid': '729fe4ae96f8...',
                             'dateCreated'  : '20190512233720'
                            }
            }

        """
        self.accAuth()
        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        # 生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = hashlib.md5(signature.encode()).hexdigest().upper()
        # 拼接URL
        url = "https://{0}:{1}/{2}/Accounts/{3}/SMS/TemplateSMS?sig={4}" \
            .format(self.ServerIP, self.ServerPort, self.SoftVersion, self.AccountSid, sig)
        # 生成auth
        src = "{0}:{1}".format(self.AccountSid, self.Batch)
        auth = base64.encodebytes(src.encode()).decode().strip()
        # 设置请求头的字典
        self.Headers["Authorization"] = auth
        self.setHttpHeader()
        # 创建请求体
        b = ''
        for a in datas:
            b += '<data>{}</data>'.format(a)

        body = '''<?xml version="1.0" encoding="utf-8"?>
                <SubAccount>
                <datas>{0}</datas>
                <to>{1}</to>
                <templateId>{2}</templateId>
                <appId>{3}</appId>
                </SubAccount>
                '''.format(b, to, tempId, self.AppId)
        if self.BodyType == 'json':
            # 如果是json类型, 则设置一下请求体
            b = datas
            body = {
                "to": to,
                "appId": self.AppId,
                "templateId": tempId,
                "datas": b
            }

        data = ''
        try:
            res = requests.post(url, headers=self.Headers, data=json.dumps(body))
            data = res.content.decode()

            if self.BodyType == 'json':
                # json格式
                locations = json.loads(data)
            else:
                # xml格式
                xtj = xmltojson()
                locations = xtj.main(data)
            if self.Iflog:
                self.log(url, body, data)
            return locations
        except Exception as error:
            if self.Iflog:
                self.log(url, body, data)
            return {'172001': '网络错误'}

    def voiceVerify(self, verifyCode, playTimes, to, displayNum, respUrl, lang, userData):
        """ 语音验证码

        Args:
            verifyCode: 必选参数  验证码内容，为数字和英文字母，不区分大小写，长度4-8位
            to:         必选参数  接收号码
            displayNum: 可选参数  显示的主叫号码
            respUrl:    可选参数  语音验证码状态通知回调地址，云通讯平台将向该Url地址发送呼叫结果通知
            lang:       可选参数  语言类型
            userData:   可选参数  第三方私有数据
        Returns:
            成功: 返回对应格式的成功响应体
            失败: 返回对应格式的失败响应体

            例如: 成功的json的响应体
            {'statusCode' : '000000',
             'templateSMS': {'smsMessageSid': '729fe4ae96f8...',
                             'dateCreated'  : '20190512233720'
                            }
            }

        """

        self.accAuth()
        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        # 生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = hashlib.md5(signature.encode()).hexdigest().upper()
        # 拼接URL
        url = "https://{0}:{1}/{2}/Accounts/{3}/Calls/VoiceVerify?sig={4}" \
            .format(self.ServerIP, self.ServerPort, self.SoftVersion, self.AccountSid, sig)
        # 生成auth
        src = "{0}:{1}".format(self.AccountSid, self.Batch)
        auth = base64.encodebytes(src.encode()).decode().strip()
        # 设置请求头的字典
        self.Headers["Authorization"] = auth
        self.setHttpHeader()

        # 创建包体
        body = '''<?xml version="1.0" encoding="utf-8"?>
                <VoiceVerify>
                <appId>{0}</appId>
                <verifyCode>{1}</verifyCode>
                <playTimes>{2}</playTimes>
                <to>{3}</to>
                <respUrl>{4}</respUrl>
                <displayNum>{5}</displayNum>
                <lang>{6}</lang>
                <userData>{7}</userData>
                </VoiceVerify>
                '''.format(self.AppId, verifyCode, playTimes, to, respUrl, displayNum, lang, userData)
        if self.BodyType == 'json':
            # 如果是json类型, 则设置一下请求体
            body = {
                "appId": self.AppId,
                "verifyCode": verifyCode,
                "playTimes": playTimes,
                "to": to,
                "respUrl": respUrl,
                "displayNum": displayNum,
                "lang": lang,
                "userData": userData
            }

        data = ''
        try:
            res = requests.post(url, headers=self.Headers, data=json.dumps(body))
            data = res.content.decode()

            if self.BodyType == 'json':
                # json格式
                locations = json.loads(data)
            else:
                # xml格式
                xtj = xmltojson()
                locations = xtj.main(data)
            if self.Iflog:
                self.log(url, body, data)
            return locations
        except Exception as error:
            if self.Iflog:
                self.log(url, body, data)
            return {'172001': '网络错误'}

    def QuerySMSTemplate(self, templateId):
        """ 短信模板查询

        Args:
            templateId: 必选参数 模板Id，如不带此参数, 则查询全部可用模板
        Retruns:
            成功: 返回成功的响应信息, XML或json格式
            失败: 返回失败的响应信息, XML或json格式

        """
        self.accAuth()
        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        # 生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = hashlib.md5(signature.encode()).hexdigest().upper()
        # 拼接URL
        url = "https://{0}:{1}/{2}/Accounts/{3}/SMS/QuerySMSTemplate?sig={4}" \
            .format(self.ServerIP, self.ServerPort, self.SoftVersion, self.AccountSid, sig)
        # 生成auth
        src = "{0}:{1}".format(self.AccountSid, self.Batch)
        auth = base64.encodebytes(src.encode()).decode().strip()
        # 设置请求头的字典
        self.Headers["Authorization"] = auth
        self.setHttpHeader()

        # 创建包体
        body = '''<?xml version="1.0" encoding="utf-8"?>
                <Request>
                <appId>{0}</appId>
                <templateId>{1}</templateId>
                </Request>
                '''.format(self.AppId, templateId)
        if self.BodyType == 'json':
            # 如果是json类型, 则设置一下请求体
            body = {
                "appId": self.AppId,
                "templateId": templateId
            }

        data = ''
        try:
            res = requests.post(url, headers=self.Headers, data=json.dumps(body))
            data = res.content.decode()

            if self.BodyType == 'json':
                # json格式
                locations = json.loads(data)
            else:
                # xml格式
                xtj = xmltojson()
                locations = xtj.main2(data)
            if self.Iflog:
                self.log(url, body, data)
            return locations
        except Exception as error:
            if self.Iflog:
                self.log(url, body, data)
            return {'172001': '网络错误'}

    def CallResult(self, callSid):
        """ 呼叫结果查询

        Args:
            callsid: 必选参数 呼叫ID
        Retruns:
            成功: 返回成功的响应信息, XML或json格式
            失败: 返回失败的响应信息, XML或json格式

        """
        self.accAuth()
        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        # 生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = hashlib.md5(signature.encode()).hexdigest().upper()
        # 拼接URL
        url = "https://{0}:{1}/{2}/Accounts/{3}/CallResult?sig={4}" \
            .format(self.ServerIP, self.ServerPort, self.SoftVersion, self.AccountSid, sig)
        # 生成auth
        src = "{0}:{1}".format(self.AccountSid, self.Batch)
        auth = base64.encodebytes(src.encode()).decode().strip()
        # 设置请求头的字典
        self.Headers["Authorization"] = auth
        self.setHttpHeader()

        data = ''
        try:
            res = requests.post(url, headers=self.Headers, data=json.dumps(body))
            data = res.content.decode()

            if self.BodyType == 'json':
                # json格式
                locations = json.loads(data)
            else:
                # xml格式
                xtj = xmltojson()
                locations = xtj.main(data)
            if self.Iflog:
                self.log(url, body, data)
            return locations
        except Exception as error:
            if self.Iflog:
                self.log(url, body, data)
            return {'172001': '网络错误'}

    def QueryCallState(self, callid, action):
        """ 呼叫状态查询

        Args:
            callid: 必选参数  一个由32个字符组成的电话唯一标识符
            action: 可选参数  查询结果通知的回调url地址
        Retruns:
            成功: 返回成功的响应信息, XML或json格式
            失败: 返回失败的响应信息, XML或json格式

        """
        self.accAuth()
        nowdate = datetime.datetime.now()
        self.Batch = nowdate.strftime("%Y%m%d%H%M%S")
        # 生成sig
        signature = self.AccountSid + self.AccountToken + self.Batch
        sig = hashlib.md5(signature.encode()).hexdigest().upper()
        # 拼接URL
        url = "https://{0}:{1}/{2}/Accounts/{3}/ivr/call?sig={4}" \
            .format(self.ServerIP, self.ServerPort, self.SoftVersion, self.AccountSid, sig)
        # 生成auth
        src = "{0}:{1}".format(self.AccountSid, self.Batch)
        auth = base64.encodebytes(src.encode()).decode().strip()
        # 设置请求头的字典
        self.Headers["Authorization"] = auth
        self.setHttpHeader()

        # 创建包体
        body = '''<?xml version="1.0" encoding="utf-8"?>
                <Request>
                <Appid>{0}</Appid>
                <QueryCallState callid="{1}" action="{2}"/>
                </Request>
                '''.format(self.AppId, callid, action)
        if self.BodyType == 'json':
            # 如果是json类型, 则设置一下请求体
            body = {
                "Appid": self.AppId,
                "QueryCallState": {"callid": callid, "action": action}
            }

        data = ''
        try:
            res = requests.post(url, headers=self.Headers, data=json.dumps(body))
            data = res.content.decode()

            if self.BodyType == 'json':
                # json格式
                locations = json.loads(data)
            else:
                # xml格式
                xtj = xmltojson()
                locations = xtj.main(data)
            if self.Iflog:
                self.log(url, body, data)
            return locations
        except Exception as error:
            if self.Iflog:
                self.log(url, body, data)
            return {'172001': '网络错误'}

    # 子帐号鉴权
    def subAuth(self):
        if(self.ServerIP == ""):
            print('172004')
            print('IP为空')

        if(self.ServerPort <= 0):
            print('172005')
            print('端口错误（小于等于0）')

        if(self.SoftVersion == ""):
            print('172013')
            print('版本号为空')

        if(self.SubAccountSid == ""):
            print('172008')
            print('子帐号为空')

        if(self.SubAccountToken == ""):
            print('172009')
            print('子帐号令牌为空')

        if(self.AppId == ""):
            print('172012')
            print('应用ID为空')

    # 主帐号鉴权
    def accAuth(self):
        if(self.ServerIP == ""):
            print('172004')
            print('IP为空')

        if(int(self.ServerPort) <= 0):
            print('172005')
            print('端口错误（小于等于0）')

        if(self.SoftVersion == ""):
            print('172013')
            print('版本号为空')

        if(self.AccountSid == ""):
            print('172006')
            print('主帐号为空')

        if(self.AccountToken == ""):
            print('172007')
            print('主帐号令牌为空')

        if(self.AppId == ""):
            print('172012')
            print('应用ID为空')

    # 设置包头
    def setHttpHeader(self):
        """ 设置包头的格式, 默认将改变self.Headers
            您只需要调用该方法, 将自动添加对应格式的请求头, 包含如下:
            "Accept", "Content-Type", "Content-Length"
        """
        if self.BodyType == 'json':
            self.Headers["Accept"] = "application/json"
            self.Headers["Content-Type"] = "application/json;charset=utf-8"
            self.Headers["Content-Length"] = "256"
        else:
            self.Headers["Accept"] = "application/xml"
            self.Headers["Content-Type"] = "application/xml;charset=utf-8"
            self.Headers["Content-Length"] = "256"
