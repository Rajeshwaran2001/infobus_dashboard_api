# Generated by Django 4.1.5 on 2023-03-09 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('utility', '0002_slot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='district',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='utility.district'),
        ),
    ]