# Generated by Django 4.2.1 on 2023-06-26 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_hotel', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='type',
            field=models.CharField(blank=True, choices=[('luxe', 'Luxe'), ('economy', 'Economy'), ('standard', 'Standard')], null=True),
        ),
    ]
