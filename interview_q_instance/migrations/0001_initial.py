# Generated by Django 2.1.4 on 2019-09-08 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interview_q', '0001_initial'),
        ('submission_result', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewQuestionInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interviewee_email', models.CharField(max_length=128)),
                ('submission', models.TextField(blank=True, null=True)),
                ('has_completed', models.BooleanField(default=False)),
                ('has_started', models.BooleanField(default=False)),
                ('start_time', models.DateTimeField(null=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('base_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interview_q.InterviewQuestion')),
                ('submission_result', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='submission_result.SubmissionResult')),
            ],
        ),
    ]
