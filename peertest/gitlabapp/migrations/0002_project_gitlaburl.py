# Generated by Django 5.0.6 on 2024-08-05 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitlabapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='gitlaburl',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
    ]
