# -*- coding: utf-8 -*-

# pip install pycryptodome
__author__ = 'bobby'

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes
from MxShop.settings import ali_pub_key_path, private_key_path
import json


class AliPay(object):
    """
    支付宝支付接口,生成支付的url
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())

        # 判断是正式环境还是测试环境
        if debug is True:
            # 沙箱环境的url
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            # 正式环境的url
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        """
        这个不是公共的请求参数，这个是请求参数，详细看支付宝官方文档
        :param subject:
        :param out_trade_no:
        :param total_amount:
        :param return_url:
        :param kwargs:
        :return:
        """
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        """
        按照官方文档说明生成订单信息字符串
        :param data:
        :return:
        """
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        # 每个参数之间用&隔开
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        # 开始进行签名。也就是使用私钥对上传的信息进行加密，也就是签名
        sign = self.sign(unsigned_string.encode("utf-8"))
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        """
        将参数进行排序
        :param data:
        :return:
        """
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名，生成签名字符串
        key = self.app_private_key  # 获取私钥
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名，验证返回的签名是否正确
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        # 将返回的信息进行
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":
    # 验证支付宝返回的信息是否正确
    return_url = 'https://openapi.alipaydev.com/gateway.do?app_id=2016101800719127&biz_content=%7B%22subject%22%3A%22%5Cu6d4b%5Cu8bd5%5Cu8ba2%5Cu53552%22%2C%22out_trade_no%22%3A%2220170202124%22%2C%22total_amount%22%3A100%2C%22product_code%22%3A%22FAST_INSTANT_TRADE_PAY%22%7D&charset=utf-8&method=alipay.trade.page.pay&notify_url=http%3A%2F%2F127.0.0.1%3A8000%2Falipay%2Freturn%2F&return_url=http%3A%2F%2F127.0.0.1%3A8000%2Falipay%2Freturn%2F&sign_type=RSA2&timestamp=2020-03-18+17%3A43%3A35&version=1.0&sign=CI1UbknKXRLpvMrM44ZcX8PqSEQuFHyEfiw4q8KqI8Sa8hEDdBjXpGsymeIyYRFr68IblLgotIU3ZcXgMS3sNM5kb6YvxBp0L%2BT4Fzpb4kQShDQhKoQEznD1gQsiiuxQYFVgbJI3uOIR8R9YB3czmGTtl29UhwwOGvBHq2K6KctfiMYDAatQDipXh2fIHjDhq%2FWHG0KBZ%2FZqlOkFeQAJn6uZjFT6dyw5jbVO306WQB6xNECle257w3tOh39j2jcpFklNqXhgP8b2GaMcjfZTC95vdpG3gqkvDvMGo4Y3AazDFme5bHnXo%2F5Ug%2BwyqXfB2WHKzKI6dJAsGjsP97UTjQ%3D%3D'
    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    # 去除sign
    ali_sign = query.pop("sign")[0]

    alipay = AliPay(
        # 沙箱环境的appid
        appid="2016101800719127",
        app_notify_url="http://127.0.0.1:8000/alipay/return/",
        # 私钥的位置
        app_private_key_path=private_key_path,
        # 阿里的公钥的位置
        alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        # True的话是进入沙箱的验证url
        debug=True,  # 默认False,
        # 支付成功跳转到哪个页面
        return_url="http://127.0.0.1:8000/alipay/return/"
    )
    # 返回验证信息的True或False
    for key, value in query.items():
        processed_query[key] = value[0]
    print(alipay.verify(processed_query, ali_sign))

    url = alipay.direct_pay(
        subject="iphone11ProMax",
        out_trade_no="20170202111",
        total_amount=100,
        return_url="http://127.0.0.1:8000/alipay/return/"
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    print(re_url)


