# Generated by Django 3.1.7 on 2021-03-25 02:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department_ID', models.CharField(max_length=4)),
                ('course_Number', models.CharField(max_length=10)),
                ('course_Title', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_Time', models.TimeField()),
                ('end_Time', models.TimeField()),
                ('meeting_day', models.CharField(choices=[('M', 'M'), ('T', 'T'), ('W', 'W'), ('R', 'R'), ('F', 'F'), ('MW', 'MW'), ('MWF', 'MWF'), ('TR', 'TR'), ('MWTWRF', 'MWTWRF')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_ID', models.CharField(max_length=20)),
                ('instructor', models.CharField(max_length=255)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.course')),
                ('periods', models.ManyToManyField(to='catalog.Period')),
            ],
        ),
    ]
