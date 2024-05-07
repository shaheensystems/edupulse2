# Generated by Django 5.0.1 on 2024-04-30 03:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0026_alter_studentfundsource_name'),
        ('program', '0026_alter_staffcourseofferingrelations_staff_and_more'),
        ('report', '0028_attendance_session_no_attendance_week_no'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('student', 'course_offering', 'attendance_date', 'week_no', 'session_no')},
        ),
    ]
