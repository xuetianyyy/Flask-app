from qiniu import Auth, put_file, put_data, etag, put_data
import qiniu.config


def storage(host, file_data):
    """ 上传文件到七牛云

    Args:
        host:      需要上传的对象空间域名, 如: http://image.weidong168.com
        file_data: 需要上传的文件(二进制数据)
    Returns:
        图片完整的连接地址, 如: http://image.weidong168.com/Ftn-lOypD-zqUGdSvTM0npx5c1IP

    """
    # 需要填写你的 Access Key 和 Secret Key
    access_key = '填写你的Access Key'
    secret_key = '填写你的Secret Key'

    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = '填写你的对象存储空间名'
    # 上传后保存的文件名
    key = None

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 上传在线文件
    ret, info = put_data(token, key, file_data)

    # print(ret)
    # print('=' * 50)
    # print(info)

    # 这个断言, 只是用来检查上传的文件名是不是key的值, 通常不需要
    # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)

    if info.status_code == 200:
        return '{}/{}'.format(host, ret.get('key'))
    else:
        raise Exception('图片上传至七牛云失败')


if __name__ == '__main__':
    with open('/home/xuetianyyy/桌面/douyu_img/252.jpg', 'rb') as f:
        file_data = f.read()

    storage('http://image.weidong168.com', file_data)
