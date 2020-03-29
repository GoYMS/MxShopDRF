from MxShop.settings import REGEX_MOBILE
from users.models import VerifyCode
import re
from datetime import datetime, timedelta
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.contrib.auth import get_user_model
User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化
    """
    class Meta:
        model = User
        fields = ('name', 'gender', 'birthday', 'email', 'mobile')


class SmsSerializer(serializers.Serializer):
    """
    验证手机号码
    """
    mobile = serializers.CharField(max_length=11)

    # 相当于重写mobile字段的验证，注意函数名称是 validate_+字段名
    def validate_mobile(self, mobile):
        # 验证手机号是否存在
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")
        # 验证手机号是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号非法")
        # 手机号发送的频率
        one_mintes_age = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gte=one_mintes_age, mobile=mobile):
            raise serializers.ValidationError("距离上次发送未超过60s")
        return mobile


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册
    """
    # write_only:到时候不用序列化,因为在下边已经将code字段删除了，没有这个的字段，所以不能进行序列化    label：显示在drf后台的信息
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                 # 自己设置，各个字段对应的错误信息提示，不写的话是使用默认的
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
    # 这里前端传入的是手机号，直接将手机号当做是用户的username
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     # drf自带的判断是否唯一的方法
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        #  下边这个加上后在drf后端输入密码的时候是加密的  ，write_only设置是不让返回序列化显示在drf后台上，密码容易被窃取
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    # 设置在数据库中密码是加密的
    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    # 验证验证码的对错
    def validate_code(self, code):
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            last_record = verify_records[0]
            # 设置五分钟过期
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.add_time:
                raise serializers.ValidationError("验证码过期")

            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")

        else:
            raise serializers.ValidationError("验证码错误")

    # 设置的是全局所有字段的修改
    def validate(self, attrs):
        # 将username传过来的username当做是mobile
        attrs["mobile"] = attrs["username"]
        # 删除code，因为在model中没有这个字段，所以就不能传入到数据库中
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "code", "mobile", "password")
