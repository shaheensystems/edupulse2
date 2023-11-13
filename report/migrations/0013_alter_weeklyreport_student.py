# Generated by Django 4.2.6 on 2023-11-13 03:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0015_rename_student_email_id_staff_email_id_and_more'),
        ('report', '0012_alter_weeklyreport_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyreport',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weekly_reports', to='customUser.student', verbose_name='Student'),
        ),
    ]
