# Generated by Django 2.0 on 2020-03-10 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0004_auto_20200310_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='name',
            field=models.CharField(max_length=50, verbose_name='商品名'),
        ),
        migrations.AlterField(
            model_name='goodscategorybrand',
            name='name',
            field=models.CharField(default='', help_text='品牌名', max_length=40, verbose_name='品牌名'),
        ),
    ]
