# Generated by Django 4.1.5 on 2023-02-26 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myads',
            name='bus_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='myads',
            name='route_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='myads',
            name='route_no',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]