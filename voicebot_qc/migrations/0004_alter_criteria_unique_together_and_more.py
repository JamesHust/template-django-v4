# Generated by Django 4.1.3 on 2022-12-13 03:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voicebot_qc', '0003_calllist_condition_config_alter_criteria_campaign_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='criteria',
            unique_together={('name', 'campaign')},
        ),
        migrations.AlterUniqueTogether(
            name='datainput',
            unique_together={('source', 'field')},
        ),
        migrations.AlterUniqueTogether(
            name='record',
            unique_together={('call', 'criteria')},
        ),
    ]