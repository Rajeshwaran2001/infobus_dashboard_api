# Generated by Django 4.1.5 on 2023-02-12 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_alter_franchise_mobile_no_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='franchise',
            name='mobile_no_1',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='franchise',
            name='mobile_no_2',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]