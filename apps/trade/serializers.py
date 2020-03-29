from rest_framework import serializers
import time
import random
from goods.models import Goods
from goods.serializers import GoodsSerializer
from .models import ShoppingCart, OrderInfo, OrderGoods
from MxShop.settings import private_key_path, ali_pub_key_path
from apps.utils.alipay import AliPay


class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = "__all__"


class ShopCartSerializers(serializers.Serializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    nums = serializers.IntegerField(required=True, label="数量", min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于1",
                                        "required": "请选择购买数量"
                                    })
    # goods是一个外键
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    # 重写create方法, 相当于往数据库中存数据
    def create(self, validated_data):
        # 注意此处使用的是上下文中的request
        user = self.context['request'].user
        nums = validated_data['nums']
        goods = validated_data['goods']
        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        # 此处是判断是新加的商品还是与原来存在只是添加数量的
        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)
        return existed

    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data['nums']
        instance.save()
        return instance


class OrderSerializers(serializers.ModelSerializer):
    """
    订单信息
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    post_script = serializers.CharField(allow_null=True)
    order_mount = serializers.IntegerField()

    # 支付宝请求的url
    alipay_url = serializers.SerializerMethodField(read_only=True,)

    # obj是serializer中的数据
    def get_alipay_url(self,obj):
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
            return_url="http://127.0.0.1:8000/alipay/return/"
        )
        url = alipay.direct_pay(
            subject= obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,

        )
        # 请求支付宝的url
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url

    class Meta:
        model = OrderInfo
        fields = "__all__"

    # 生成随机订单号
    def generate_order_sn(self):
        random_ins = random.Random()
        order_sn = "{0}{1}{2}".format(time.strftime("%Y%m%d%H%M%S"), self.context['request'].user,
                                      random_ins.randint(10,100))
        return order_sn

    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        return attrs


class OrderGoodsSerialzier(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerialzier(many=True)
    # 支付宝请求的url
    alipay_url = serializers.SerializerMethodField(read_only=True, )

    # obj是serializer中的数据
    def get_alipay_url(self, obj):
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
            return_url="http://127.0.0.1:8000/alipay/return/"
        )
        url = alipay.direct_pay(
            subject=obj.order_sn,
            out_trade_no=obj.order_sn,
            total_amount=obj.order_mount,

        )
        # 请求支付宝的url
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
        return re_url

    class Meta:
        model = OrderInfo
        fields = "__all__"


