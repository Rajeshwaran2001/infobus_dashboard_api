# Generated by Django 4.1.5 on 2023-03-02 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('District', '0002_alter_district_options_district_is_active'),
        ('dashboard', '0004_taskresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='franchise',
            name='district',
            field=models.ManyToManyField(blank=True, to='District.district'),
        ),
    ]