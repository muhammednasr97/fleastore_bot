# Generated by Django 3.0.1 on 2019-12-27 21:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BotUser',
            new_name='User',
        ),
    ]
