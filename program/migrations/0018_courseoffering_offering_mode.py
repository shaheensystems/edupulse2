# Generated by Django 4.2.6 on 2023-12-04 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0017_courseoffering_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseoffering',
            name='offering_mode',
            field=models.CharField(blank=True, choices=[('online', 'ONLINE'), ('offline', 'OFFLINE'), ('blended', 'BLENDED')], default='online', help_text='Select the mode of course offering: Online, Offline, or Blended', max_length=10, null=True),
        ),
    ]
