# Generated by Django 4.2.6 on 2023-10-30 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0014_alter_newuser_campus_alter_newuser_dob_and_more'),
        ('program', '0010_alter_courseoffering_course_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_efts',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='courseoffering',
            name='student',
            field=models.ManyToManyField(blank=True, related_name='course_offering', to='customUser.student'),
        ),
        migrations.AlterField(
            model_name='programoffering',
            name='student',
            field=models.ManyToManyField(blank=True, related_name='program_offering', to='customUser.student'),
        ),
    ]
