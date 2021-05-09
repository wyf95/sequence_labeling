# Generated by Django 2.2.13 on 2021-05-08 07:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_label_prefix_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100)),
                ('background_color', models.CharField(default='#209cee', max_length=7)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to='api.Project')),
            ],
            options={
                'unique_together': {('project', 'text')},
            },
        ),
        migrations.AlterField(
            model_name='connection',
            name='relation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Relation'),
        ),
        migrations.AlterUniqueTogether(
            name='connection',
            unique_together={('document', 'relation', 'source', 'to')},
        ),
    ]