from celery import Celery
from libs.YunTongXun.SendTemplateSMS import CCP


celery_app = Celery('sms_tasks', broker='redis://127.0.0.1:6379/3')


@celery_app.task
def send_sms(to, datas, tempId):
    """ 发送短信的异步任务

    Args:
        to:     str 接收者的手机号, 也可以是多个, 如: "131..., 132..., ..."
        datas:  list 或 '' 发送的内容数据列表(内容需为字符串)
                如: ['验证码', '失效分钟'] 如没有内容请填写''
        tempId: str 模板Id (免费测试的模板Id为1)
    Returns:
        成功: 0
        失败: -1

    """
    ccp = CCP()
    ccp.sendTemplateSMS(to, datas, tempId)
    return '-->发送成功'
