# Generated by Django 4.2.6 on 2023-10-26 03:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customUser', '0006_newuser_campus_staff_designation_staff_joining_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0004_alter_programoffering_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('active_status', models.BooleanField()),
                ('attended', models.BooleanField(default=False)),
                ('attendance_date', models.DateField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.course')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('program_offering', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='program.programoffering')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customUser.student')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('student', 'program_offering', 'course')},
            },
        ),
    ]
