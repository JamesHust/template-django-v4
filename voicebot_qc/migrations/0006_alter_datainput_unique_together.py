# Generated by Django 4.1.3 on 2022-12-14 08:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voicebot_qc', '0005_datainput_campaign_alter_call_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='datainput',
            unique_together={('source', 'field', 'campaign')},
        ),
    ]