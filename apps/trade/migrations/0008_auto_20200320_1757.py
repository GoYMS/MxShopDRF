# Generated by Django 2.0 on 2020-03-20 17:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0007_auto_20200318_2155'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ordergoods',
            old_name='good_nums',
            new_name='goods_num',
        ),
    ]
