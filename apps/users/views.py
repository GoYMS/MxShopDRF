from rest_framework import permissions
from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from MxShop.settings import APIKEY
from users.models import VerifyCode
from utils.yunpian import YunPian
from users.serializers import SmsSerializer, UserRegSerializer
from django.contrib.auth.backends import ModelBackend
from rest_framework import viewsets
from rest_framework import mixins
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from random import choice
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from .serializers import UserDetailSerializer
# 找到用户自定义的模板
from django.contrib.auth import get_user_model
User = get_user_model()


# ModelBackend用户认证的 ，下边重写认证方法
# 写完后需要在setting中指定这个方法
class CustomBackend(ModelBackend):
    """
    自定义用户验证,重写下边的方法
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    # 生成随机验证码
    def generate_code(self):
        """
        生成随机验证码
        :return:
        """
        seeds = '1234567890'
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return ''.join(random_str)

    # 重写create方法,好像是相当于post方法
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = serializer.validated_data['mobile']
        yun_pian = YunPian(APIKEY)
        code = self.generate_code()

        sms_status = yun_pian.send_sms(code=code, mobile=mobile)
        if sms_status['code'] != 0:
            return Response({
                'mobile': sms_status['msg']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_recose = VerifyCode(code=code, mobile=mobile)
            code_recose.save()
            return Response({
                'mobile': sms_status['msg']
            }, status=status.HTTP_201_CREATED)


class UserViewset(mixins.CreateModelMixin, viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.RetrieveModelMixin):
        """
        create：
            用户注册
        retrieve:
            用户的信息
        update:
            个人信息修改

        """
        serializer_class = UserRegSerializer
        queryset = User.objects.all()
        authentication_classes = (JSONWebTokenAuthentication, authentication.SessionAuthentication)

        # 重写这个方法， 用来判断什么时候使用哪个序列化
        def get_serializer_class(self):
            if self.action == "retrieve":
                return UserDetailSerializer
            elif self.action == "create":
                return UserRegSerializer

            return UserDetailSerializer

        # 判断用户的状态，并确定是否需要权限验证
        # permission_classes = (permissions.IsAuthenticated, )
        def get_permissions(self):
            if self.action == "retrieve":
                return [permissions.IsAuthenticated()]
            elif self.action == "create":
                return []
            return []

        # 重写这个方法，将token取出来
        def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = self.perform_create(serializer)

            re_dict = serializer.data
            payload = jwt_payload_handler(user)
            re_dict["token"] = jwt_encode_handler(payload)
            re_dict["name"] = user.name if user.name else user.username

            headers = self.get_success_headers(serializer.data)
            return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

