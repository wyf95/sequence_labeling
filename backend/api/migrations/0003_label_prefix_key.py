# Generated by Django 2.2.13 on 2021-05-08 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_remove_label_prefix_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='label',
            name='prefix_key',
            field=models.CharField(blank=True, choices=[('ctrl', 'ctrl'), ('shift', 'shift'), ('ctrl shift', 'ctrl shift')], max_length=10, null=True),
        ),
    ]