from datetime import datetime
from goods.models import Goods
from django.db import models
# 找到用户自定义的模板
from django.contrib.auth import get_user_model
User = get_user_model()


class UserFav(models.Model):
    """
    用户收藏
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='用户')
    goods = models.ForeignKey(Goods,on_delete=models.CASCADE, verbose_name="商品")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加的时间")

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name
        # 联合唯一 ，也就是对应的这两条数据只能有一条相互对应
        unique_together = ('user', 'goods')

    def __str__(self):
        return self.user.username


class UserLeavingMessage(models.Model):
    """
    用户留言
    """
    MESSAGE_CHOICES = (
        (1, "留言"),
        (2, "投诉"),
        (3, "询问"),
        (4, "售后"),
        (5, "求购")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    message_type = models.CharField(choices=MESSAGE_CHOICES, max_length=10, verbose_name="留言",
                                    help_text="留言类型：1.留言 2.投诉 3.询问 4.售后 5.求购")
    subject = models.CharField(max_length=100, default="", verbose_name="主题")
    message = models.TextField(default="", verbose_name="留言内容", help_text="留言内容")
    file = models.FileField(verbose_name="上传的文件", help_text="上传的文件")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加的时间")

    class Meta:
        verbose_name = "用户留言"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.subject


class UserAddress(models.Model):
    """
    用户的收货地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    province = models.CharField(max_length=100, default="", verbose_name="省份")
    city = models.CharField(max_length=100, default="", verbose_name="城市")
    district = models.CharField(max_length=100, default="", verbose_name="区域")
    address = models.CharField(max_length=100, default="", verbose_name="详细地址")
    signer_name = models.CharField(max_length=20, default="", verbose_name="签收人")
    signer_mobile = models.CharField(max_length=11, verbose_name="手机号码")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加的时间")

    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.address


