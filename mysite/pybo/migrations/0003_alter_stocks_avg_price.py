# Generated by Django 3.2.16 on 2022-10-25 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0002_auto_20221025_0947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocks',
            name='avg_price',
            field=models.FloatField(),
        ),
    ]
