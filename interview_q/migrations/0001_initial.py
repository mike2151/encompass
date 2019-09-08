# Generated by Django 2.1.4 on 2019-09-08 18:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api_q', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewQuestion',
            fields=[
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('time_limit_minutes', models.IntegerField(default=60)),
                ('language', models.CharField(default='Python3', max_length=128)),
                ('starter_code', models.TextField(null=True)),
                ('solution', models.TextField(null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_open', models.BooleanField(default=False)),
                ('api', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api_q.InterviewAPI')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
