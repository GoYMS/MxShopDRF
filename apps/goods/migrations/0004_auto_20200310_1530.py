# Generated by Django 2.0 on 2020-03-10 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_auto_20200310_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodscategorybrand',
            name='image',
            field=models.ImageField(max_length=200, upload_to='brand/', verbose_name='品牌封面'),
        ),
    ]