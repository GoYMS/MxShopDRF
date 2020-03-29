import requests
import json
from MxShop.settings import APIKEY


class YunPian(object):
    """
    云片网发送短信相关设置
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = 'https://sms.yunpian.com/v2/sms/single_send.json'

    def send_sms(self, code, mobile):
        parmas = {
            'apikey': self.api_key,
            'mobile': mobile,
            'text': '【李皓琳】您的验证码是{0}。如非本人操作，请忽略本短信'.format(code)
        }
        response = requests.post(self.url, data=parmas)
        re_dict = json.loads(response.text)
        return re_dict


if __name__ == '__main__':
    yunpian = YunPian(APIKEY)
    yunpian.send_sms('2020', '15515819567')


