# Generated by Django 2.2.4 on 2019-09-10 11:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('example_code', '0002_auto_20190909_2138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examplecode',
            name='body',
        ),
    ]
