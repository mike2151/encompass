# Generated by Django 2.2.4 on 2019-11-11 17:03

from django.db import migrations, models
import interview_q.models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q', '0013_auto_20191111_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewquestion',
            name='id',
            field=models.CharField(default=interview_q.models.make_uuid, max_length=16, primary_key=True, serialize=False),
        ),
    ]