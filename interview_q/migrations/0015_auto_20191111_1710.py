# Generated by Django 2.2.4 on 2019-11-11 17:10

from django.db import migrations, models
import interview_q.models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q', '0014_auto_20191111_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewquestion',
            name='id',
            field=models.IntegerField(default=interview_q.models.make_pk, primary_key=True, serialize=False),
        ),
    ]
