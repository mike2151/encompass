# Generated by Django 2.2.4 on 2019-09-16 23:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q', '0003_auto_20190910_1115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewquestion',
            name='api',
        ),
    ]