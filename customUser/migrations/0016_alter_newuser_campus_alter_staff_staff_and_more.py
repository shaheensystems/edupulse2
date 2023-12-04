# Generated by Django 4.2.6 on 2023-12-04 00:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_address_id_alter_campus_id'),
        ('customUser', '0015_rename_student_email_id_staff_email_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newuser',
            name='campus',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='base.campus', verbose_name='Campus'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='student',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to=settings.AUTH_USER_MODEL),
        ),
    ]
