# Generated by Django 4.2.6 on 2023-12-05 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0020_alter_staff_designation'),
        ('program', '0018_courseoffering_offering_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='programoffering',
            name='program_leader',
            field=models.ManyToManyField(blank=True, null=True, related_name='program_offerings', to='customUser.staff'),
        ),
    ]
