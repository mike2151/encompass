# Generated by Django 2.2.4 on 2019-11-11 17:13

from django.db import migrations, models
import interview_q_instance.models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q_instance', '0011_interviewquestioninstance_interviewee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewquestioninstance',
            name='id',
            field=models.IntegerField(default=interview_q_instance.models.make_pk, primary_key=True, serialize=False),
        ),
    ]
