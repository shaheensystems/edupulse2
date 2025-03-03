# Generated by Django 4.2.6 on 2023-11-07 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0014_alter_newuser_campus_alter_newuser_dob_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='staff',
            old_name='student_email_id',
            new_name='email_id',
        ),
        migrations.AlterField(
            model_name='staff',
            name='designation',
            field=models.CharField(blank=True, choices=[('Admin', 'Admin'), ('HR', 'Human Resources'), ('Lecturer', 'Lecturer'), ('Assistant Lecturer', 'Assistant Lecturer'), ('Counselor', 'Counselor')], max_length=255, null=True),
        ),
    ]
