# Generated by Django 2.2.4 on 2019-09-25 00:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteuser',
            old_name='is_interview_creator',
            new_name='is_from_company',
        ),
    ]