# Generated by Django 3.1.7 on 2021-04-16 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20210416_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artileupdown',
            name='is_up',
            field=models.BooleanField(default=True, verbose_name='是否点赞'),
        ),
    ]