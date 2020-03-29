from datetime import datetime
from django.db import models
# 使用自定义的user用户
from django.contrib.auth.models import AbstractUser


# 继承自定义的类，但是还包括的有django自带的auth类
class UserProfile(AbstractUser):  # 写完之后需要在setting中注册
    """
    用户
    """
    # 在注册用户的时候，是使用手机号码登录验证，所以最开始没有名字和生日，所以可以为空
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="手机号")
    gender = models.CharField(max_length=6, choices=(('male', '男'), ('female', '女')), default='female',verbose_name="性别")
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    # 元类
    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    # 类返回的值  魔法函数
    def __str__(self):
        return self.username


class VerifyCode(models.Model):
    """
    存储短信验证码
    """
    code = models.CharField(max_length=10, verbose_name="验证码")
    mobile = models.CharField(max_length=11, verbose_name="手机号")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="注册时间")

    class Meta():
        verbose_name = "验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code

