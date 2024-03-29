# Generated by Django 3.2.4 on 2021-06-05 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restapi', '0003_move'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='end_time',
            field=models.DateTimeField(blank=True, help_text='Time at which the game was completed.', null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='start_time',
            field=models.DateTimeField(blank=True, help_text='Time at which the user made the first move.', null=True),
        ),
    ]
