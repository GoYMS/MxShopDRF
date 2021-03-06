# Generated by Django 2.0 on 2020-03-09 22:46

import DjangoUeditor.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodscategorybrand',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='goods.GoodsCategory', verbose_name='商品类别'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='goods_desc',
            field=DjangoUeditor.models.UEditorField(default='', verbose_name='商品主要内容'),
        ),
    ]
