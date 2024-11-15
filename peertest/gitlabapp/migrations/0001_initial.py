# Generated by Django 5.0.6 on 2024-08-05 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('original_project_id', models.IntegerField()),
                ('namespace', models.CharField(max_length=255)),
                ('gitlabaccesstoken', models.CharField(max_length=255)),
                ('members', models.JSONField(null=True)),
                ('branches', models.JSONField(null=True)),
                ('testingproject', models.JSONField(null=True)),
                ('commits', models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestInstance',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('commit_id', models.CharField(max_length=255)),
                ('project_id', models.CharField(max_length=255)),
                ('gitlabaccesstoken', models.CharField(max_length=255)),
                ('branchname', models.CharField(max_length=255)),
            ],
        ),
    ]
