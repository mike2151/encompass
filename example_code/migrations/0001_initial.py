# Generated by Django 2.2.4 on 2019-09-08 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('interview_q', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExampleCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('interview_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='interview_q.InterviewQuestion')),
            ],
        ),
    ]
