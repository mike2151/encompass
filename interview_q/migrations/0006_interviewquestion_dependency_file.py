# Generated by Django 2.2.4 on 2019-10-19 22:22

from django.db import migrations, models
import interview_q.models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q', '0005_interviewquestion_network_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewquestion',
            name='dependency_file',
            field=models.FileField(null=True, upload_to=interview_q.models.InterviewQuestion.upload_path_handler),
        ),
    ]
