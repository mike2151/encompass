# Generated by Django 2.2.4 on 2019-09-30 01:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q_instance', '0006_interviewquestioninstance_can_preview'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewquestioninstance',
            name='submission',
        ),
    ]
