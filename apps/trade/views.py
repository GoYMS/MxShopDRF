from rest_framework import viewsets
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime


from utils.permissions import IsOwnerOrReadOnly
from trade.serializers import ShopCartSerializers, ShopCartDetailSerializer, OrderSerializers
from trade.serializers import OrderDetailSerializer
from trade.models import ShoppingCart, OrderInfo, OrderGoods
from MxShop.settings import ali_pub_key_path, private_key_path
from apps.utils.alipay import AliPay
from django.shortcuts import redirect


class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    list:
       购物车信息
    retrieve:
        购物车详细信息
    create：
        添加购物车
    destroy：
        删除购物车信息
    """
    # authentication是身份认证，判断当前用户的登录方式是哪种认证方式
    # permissions是权限认证，判断哪些用户有操作权限
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # 通过goods的id操作
    lookup_field = "goods_id"

    # 只显示登录用户的购物车信息
    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    # serializer动态显示
    def get_serializer_class(self):
        if self.action == "list":
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializers

    # 加入购物车库存剩余量减一
    def perform_create(self, serializer):
        shop_cart = serializer.save()
        goods = shop_cart.goods
        goods.goods_num -= shop_cart.nums
        goods.save()

    # 去除购物车
    def perform_destroy(self, instance):
        goods = instance.goods
        goods.goods_num += instance.nums
        goods.save()
        instance.delete()

    # 在购物车中添加删除数量
    def perform_update(self, serializer):

        # 哪个商品数量改变
        existed_recorde = ShoppingCart.objects.get(id=serializer.instance.id)
        existed_nums = existed_recorde.nums
        saved_record = serializer.save()
        # 保存后的数量减去保存前的数量
        nums = saved_record.nums-existed_nums
        goods = saved_record.goods
        goods.goods_num -= nums
        goods.save()


class OrderViewset(viewsets.ModelViewSet):
    """
    订单管理
    """
    # authentication是身份认证，判断当前用户的登录方式是哪种认证方式
    # permissions是权限认证，判断哪些用户有操作权限
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            return OrderSerializers

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.good_nums = shop_cart.nums
            order_goods.order = order
            order_goods.save()
            # 如果生成订单号后，购物车就会清空
            shop_cart.delete()
        return order


# class AlipayView(APIView):
#
#     def get(self, request):
#         """
#         return_url
#         处理支付完成后跳转的页面,同样加上判断支付宝返回的信息是否正确
#         :param request:
#         :return:
#         """
#         processed_dict = {}
#         for key, value in request.GET.items():
#             processed_dict[key] = value
#
#         sign = processed_dict.pop("sign", None)
#
#         alipay = AliPay(
#             appid="2016101800719127",
#             app_notify_url="http://127.0.0.1:8000/alipay/return/",
#             app_private_key_path=private_key_path,
#             alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
#             debug=True,  # 默认False,
#             return_url="http://127.0.0.1:8000/alipay/return/"
#         )
#
#         verify_re = alipay.verify(processed_dict, sign)
#
#         if verify_re is True:
#             # order_sn = processed_dict.get('out_trade_no', None)
#             # trade_no = processed_dict.get('trade_no', None)
#             # trade_status = processed_dict.get('trade_status', None)
#             #
#             # existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
#             # for existed_order in existed_orders:
#             #     existed_order.pay_status = trade_status
#             #     existed_order.trade_no = trade_no
#             #     existed_order.pay_time = datetime.now()
#             #     existed_order.save()
#
#             response = redirect("index")
#             # 如果支付成功，跳转到订单页面
#             response.set_cookie("nextPath", "pay", max_age=3)
#             return response
#         else:
#             response = redirect("index")
#             return response
#
#     def post(self,request):
#         """
#         notify_url
#         处理扫码后不支付，支付宝应该将订单状态传入到哪个页面中
#         """
#         # 将支付宝返回的信息后边的参数进行拆分
#         processed_dict = {}
#         for key, value in request.POST.items():
#             processed_dict[key] = value
#         # 将sign取出
#         sign = processed_dict.pop("sign", None)
#         #
#         alipay = AliPay(
#             appid="2016101800719127",
#             app_notify_url="http://127.0.0.1:8000/alipay/return/",
#             app_private_key_path=private_key_path,
#             alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
#             debug=True,  # 默认False,
#             return_url="http://127.0.0.1:8000/alipay/return/"
#         )
#         # 判断支付宝返回的信息是否正确，看是否被篡改
#         verify_re = alipay.verify(processed_dict, sign)
#
#         if verify_re is True:
#             # 如果正确，将其中的信息取出
#             order_sn = processed_dict.get('out_trade_no', None)
#             trade_no = processed_dict.get('trade_no', None)
#             trade_status = processed_dict.get('trade_status', None)
#             # 保存到数据库中
#             existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
#             for existed_order in existed_orders:
#                 # order_goods = existed_order.goods.all()
#                 # for order_good in order_goods:
#                 #     goods = order_good.goods
#                 #     goods.sold_num += order_good.goods_num
#                 #     goods.save()
#
#                 existed_order.pay_status = trade_status
#                 existed_order.trade_no = trade_no
#                 existed_order.pay_time = datetime.now()
#                 existed_order.save()
#
#             # 给支付宝返回成功。要不然支付宝会一直向我们请求
#             return Response("success")
#
class AlipayView(APIView):
    def get(self, request):
        """
        处理支付宝的return_url返回
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            appid="",
            app_notify_url="http://127.0.0.1:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/return/"
        )

        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                existed_order.pay_status = 'TRADE_SUCCESS'
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            response = redirect("index")
            response.set_cookie("nextPath", "pay", max_age=3)
            return response
        else:
            response = redirect("index")
            return response

    def post(self, request):
        """
        处理支付宝的notify_url
        :param request:
        :return:
        """
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value

        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            appid="",
            app_notify_url="http://127.0.0.1:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            debug=True,  # 默认False,
            return_url="http://127.0.0.1:8000/alipay/return/"
        )

        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()

                existed_order.pay_status = 'TRADE_SUCCESS'
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            return Response("success")




