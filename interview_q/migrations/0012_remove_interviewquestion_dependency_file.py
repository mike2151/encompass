# Generated by Django 2.2.4 on 2019-10-30 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q', '0011_interviewquestion_dependency_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewquestion',
            name='dependency_file',
        ),
    ]
