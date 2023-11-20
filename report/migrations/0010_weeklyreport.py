# Generated by Django 4.2.6 on 2023-11-09 03:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0014_alter_courseoffering_course'),
        ('customUser', '0015_rename_student_email_id_staff_email_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('report', '0009_alter_attendance_is_present'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeklyReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('temp_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('active_status', models.BooleanField(default=True)),
                ('week_number', models.PositiveIntegerField(blank=True, null=True)),
                ('session_number', models.PositiveIntegerField(blank=True, null=True)),
                ('engagement', models.CharField(blank=True, choices=[('na', 'N/A'), ('on track canvas', 'On Track - CANVAS'), ('on track assessment', 'On Track - Assessment'), ('on track learning activity', 'On Track - Learning Activity'), ('on track blended', 'On Track - Blended'), ('not engaged', 'Not Engaged')], default='N/A', max_length=255, null=True)),
                ('action', models.CharField(blank=True, choices=[('na', 'N/A'), ('follow up email and call', 'Follow Up Email and Call'), ('pastoral care', 'Pastoral Care'), ('personalised study plan/Extra session', 'Personlaised Study Plan /Extra Session'), ('emergency contact', 'Emergency Contact'), ('other', 'Other')], max_length=255, null=True)),
                ('follow_up', models.CharField(blank=True, choices=[('na', 'N/A'), ('warning letter 1', 'Warning Letter 1'), ('warning letter 2', 'Warning Letter 2')], max_length=255, null=True)),
                ('course_offering', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_reports', to='program.courseoffering', verbose_name='Course Offering')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_reports', to='customUser.student', verbose_name='Course Offering')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
