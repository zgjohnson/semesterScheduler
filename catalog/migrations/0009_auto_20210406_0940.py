# Generated by Django 3.1.7 on 2021-04-06 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_reservedtime_reserved_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservedtime',
            name='reserved_Day',
            field=models.CharField(choices=[('M', 'Monday'), ('T', 'Tuesday'), ('W', 'Wednesday'), ('R', 'Thursday'), ('F', 'Friday')], default='', max_length=5),
        ),
    ]
