# Generated by Django 2.2.4 on 2019-09-27 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190927_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptioncouponcode',
            name='description',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
