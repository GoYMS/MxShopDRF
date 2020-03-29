from rest_framework import mixins
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from user_operation.serializers import UserFavSerializer, UserFavDetailSerializer, LeavingMessageSerializer
from user_operation.serializers import UserAddressSerializer
from .models import UserFav, UserLeavingMessage, UserAddress
from utils.permissions import IsOwnerOrReadOnly
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class UserFavViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    create:
        用户收藏功能
    list:
        用户收藏的商品
    retrieve:
        商品的信息
    destroy:
        取消收藏
    """
    serializer_class = UserFavSerializer
    # authentication是身份认证，判断当前用户的登录方式是哪种认证方式
    # permissions是权限认证，判断哪些用户有操作权限
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'goods_id'

    # 只返回自己用户对应的收藏信息
    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)

    # 重写 收藏数加1
    def perform_create(self, serializer):
        instance = serializer.save()
        goods = instance.goods
        goods.fav_num += 1
        goods.save()

    # 用户取消收藏
    def perform_destroy(self, instance):

        goods = instance.goods
        goods.fav_num -= 1
        goods.save()
        instance.delete()

    # 重写这个方法， 用来判断什么时候使用哪个序列化
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        elif self.action == "create":
            return UserFavSerializer

        return UserFavSerializer


class LeavingMessageSerializerViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                               mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    list:
        展示留言信息
    retrieve:
        留言具体信息
    create：
        添加留言信息
    destroy：
        删除留言信息
    """
    serializer_class = LeavingMessageSerializer

    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


class UserAddressViewset(viewsets.ModelViewSet):
    """
    list:
        用户收货地址
    retrieve:
        收货地址信息
    create：
        添加收货地址
    destroy：
        删除收货地址
    """
    serializer_class = UserAddressSerializer

    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
