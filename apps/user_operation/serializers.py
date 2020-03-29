from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from user_operation.models import UserFav, UserLeavingMessage, UserAddress
from goods.serializers import GoodsSerializer


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户收货地址
    """
    # 获取当前登陆的用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    signer_mobile = serializers.CharField(max_length=11, min_length=11, allow_null=False, help_text='手机号',
                                          error_messages={
                                            "allow_null": '手机号不能为空',
                                            'max_length': '手机号不规范',
                                            'min_length': '手机号不规范'
                                        })
    signer_name = serializers.CharField(allow_null=False, error_messages={"allow_null": '不能为空'})

    class Meta:
        model = UserAddress
        fields = ('user',  'id', 'province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'add_time')


class LeavingMessageSerializer(serializers.ModelSerializer):
    """
    用户留言
    """
    # 获取当前登陆的用户
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = ('user', 'message_type', 'subject', 'message', 'file', 'id', 'add_time')


class UserFavDetailSerializer(serializers.ModelSerializer):
    """
    用户收藏的详细信息
    """
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ('goods', 'id')


class UserFavSerializer(serializers.ModelSerializer):
    # 查找到当前登陆的用户,如果不加这个，在drf的后台中就会出现选择用户，这是不合理的
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    # 将user和good的字段联合在一起，对应的字段是唯一的，也就是防止一个用户点击的收藏一个商品后，再点击还能收藏
    # 可以在model中进行设置，这里可以，两者都写了，这里边会覆盖掉model中的
    validators = [
        UniqueTogetherValidator(
            queryset=UserFav.objects.all(),
            fields=('user', 'goods'),
            message="已经收藏"
        )
    ]

    class Meta:
        model = UserFav
        fields = ('user', 'goods', 'id')


