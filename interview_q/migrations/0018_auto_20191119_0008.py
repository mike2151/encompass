# Generated by Django 2.2.4 on 2019-11-19 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview_q', '0017_auto_20191118_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interviewquestion',
            name='banned_imports',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='interviewquestion',
            name='dependencies',
            field=models.TextField(blank=True, null=True),
        ),
    ]
