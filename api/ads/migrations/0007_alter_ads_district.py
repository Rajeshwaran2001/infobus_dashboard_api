# Generated by Django 4.1.5 on 2023-03-02 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('District', '0002_alter_district_options_district_is_active'),
        ('ads', '0006_remove_ads_district_ads_district'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ads',
            name='District',
            field=models.ManyToManyField(blank=True, to='District.district'),
        ),
    ]
