# Generated by Django 4.1.3 on 2022-11-22 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voicebot_qc', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='calllist',
            unique_together={('name', 'campaign')},
        ),
    ]