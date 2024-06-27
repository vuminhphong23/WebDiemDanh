# Generated by Django 5.0.6 on 2024-06-27 16:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('class_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_name', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=100)),
                ('teacher', models.ForeignKey(limit_choices_to={'is_superuser': False}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceSession',
            fields=[
                ('session_id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_sessions', to='authentication.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='TblStudents',
            fields=[
                ('student_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=100, unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('iCap', models.BooleanField(default=False)),
                ('date_birth', models.DateField()),
                ('password', models.CharField(default='pbkdf2_sha256$720000$FE8jHogT41HqidDAx1kH3v$Hr/XxxlCEVHOd/uKHLstmicPPTm/l3gHUYfq0Ml2vDk=', max_length=128)),
                ('classrooms', models.ManyToManyField(blank=True, related_name='students', to='authentication.classroom')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attended', models.BooleanField(default=False)),
                ('date', models.DateField(blank=True, null=True)),
                ('time', models.TimeField(blank=True, null=True)),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='authentication.attendancesession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='authentication.tblstudents')),
            ],
        ),
    ]
