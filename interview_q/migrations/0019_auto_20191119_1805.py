# Generated by Django 2.2.4 on 2019-11-19 18:05

from django.db import migrations, models
import interview_q.models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q', '0018_auto_20191119_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewquestion',
            name='id',
            field=models.BigIntegerField(default=interview_q.models.make_pk, primary_key=True, serialize=False),
        ),
    ]
