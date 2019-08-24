
#Flask配置
DEBUG = True

REG_PATH = 'Avatar'

#Mongodb数据库

from pymongo import MongoClient
MC = MongoClient('127.0.0.1',27017)
MongoDB = MC['Talk']

# 返回值配置
RET = {
    "code": 0,
    'data': {}
}

# 联图二维码接口
LT_URL = "http://qr.liantu.com/api.php?text=%s"
# 图灵机器人
TL = "http://openapi.tuling123.com/openapi/api/v2"