# Generated by Django 3.2.16 on 2022-10-25 00:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stocks',
            name='create_date',
        ),
        migrations.RemoveField(
            model_name='stocks',
            name='now_price',
        ),
    ]
