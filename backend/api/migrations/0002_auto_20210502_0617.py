# Generated by Django 2.2.13 on 2021-05-01 22:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sequenceannotation',
            name='connections',
        ),
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doc_conn', to='api.Document')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conn_source', to='api.SequenceAnnotation')),
                ('to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conn_to', to='api.SequenceAnnotation')),
            ],
        ),
    ]
