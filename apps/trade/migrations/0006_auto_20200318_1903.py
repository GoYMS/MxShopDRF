# Generated by Django 2.0 on 2020-03-18 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0005_auto_20200317_2033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordergoods',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='trade.OrderInfo', verbose_name='商品订单'),
        ),
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('WAIT_BUYER_PAY', '交易创建'), ('TRADE_CLOSED', '超时关闭'), ('TRADE_SUCCESS', '交易成功'), ('TRADE_FINISHED', '交易结束'), ('paying', '待支付')], default='paying', max_length=30, verbose_name='订单状态'),
        ),
    ]
