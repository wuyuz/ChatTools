
#Flask配置
from aip import AipSpeech

DEBUG = True

#路径
REG_PATH = 'Avatar'
CHAT_PATH = 'Audio'

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

TL_DATA = {
    "perception": {
        "inputText": {
            "text": "",
        }
    },
    "userInfo": {
        "apiKey": "51ff3d2dd9464ba6bba97ff1bb9427ab",
        "userId": "123456789123"
    }
}

APP_ID = '16981704'
API_KEY = 'CeLs5zCuQwWXBhHbrnDGQhc3'
SECRET_KEY = 'HIOyvsDRcXKlP95NOY72CAUznUIC6OKZ'

AUDIO_CLIENT = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

VOICE = {
    'vol': 5,
    'spd': 4,
    'pit': 6,
    'per': 4
}