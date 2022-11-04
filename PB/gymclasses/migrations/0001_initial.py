# Generated by Django 4.1.3 on 2022-11-03 00:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('studios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GymClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('keywords', models.TextField()),
                ('capacity', models.IntegerField()),
                ('studio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='studios.studio')),
            ],
        ),
        migrations.CreateModel(
            name='GymClassSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=9)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='GymClassOccurence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('enrollment_capacity', models.IntegerField()),
                ('enrollment_count', models.IntegerField()),
                ('parent_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gymclasses.gymclass')),
            ],
        ),
        migrations.AddField(
            model_name='gymclass',
            name='weekly_schedule',
            field=models.ManyToManyField(to='gymclasses.gymclassschedule'),
        ),
    ]