# Generated by Django 2.0 on 2020-03-16 10:12

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('goods', '0006_hotsearchwords_indexad'),
        ('user_operation', '0002_auto_20200309_2057'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userfav',
            unique_together={('user', 'goods')},
        ),
    ]
