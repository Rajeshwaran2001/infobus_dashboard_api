# Generated by Django 4.1.5 on 2023-03-11 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='office',
            name='mobile_no_1',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
