# Generated by Django 4.1.5 on 2023-03-07 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0009_alter_ads_display'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ads',
            old_name='AdNameTamil',
            new_name='AdNameUsername',
        ),
    ]
