# Generated by Django 4.1.5 on 2023-03-05 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0007_alter_ads_district'),
    ]

    operations = [
        migrations.AddField(
            model_name='ads',
            name='display',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='ads',
            name='AdNameTamil',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
