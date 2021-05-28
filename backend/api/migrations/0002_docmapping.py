# Generated by Django 2.2.13 on 2021-05-28 06:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Document')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doc_mappings', to='api.Project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doc_mappings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('project', 'user', 'document')},
            },
        ),
    ]
