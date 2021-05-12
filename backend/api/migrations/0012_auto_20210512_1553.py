# Generated by Django 2.2.13 on 2021-05-12 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_document_relation_concordance'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='entity_concordance',
            field=models.DecimalField(decimal_places=4, default=1.0, max_digits=6),
        ),
        migrations.AddField(
            model_name='project',
            name='relation_concordance',
            field=models.DecimalField(decimal_places=4, default=1.0, max_digits=6),
        ),
    ]
