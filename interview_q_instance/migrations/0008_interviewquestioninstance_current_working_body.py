# Generated by Django 2.2.4 on 2019-10-02 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q_instance', '0007_remove_interviewquestioninstance_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewquestioninstance',
            name='current_working_body',
            field=models.TextField(blank=True, null=True),
        ),
    ]
