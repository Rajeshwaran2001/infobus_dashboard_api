# Generated by Django 4.1.5 on 2023-01-31 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('District', models.CharField(blank=True, max_length=20, null=True)),
                ('DistrictTamil', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
