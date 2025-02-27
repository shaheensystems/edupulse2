# Generated by Django 4.2.6 on 2023-11-22 01:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploadFile', '0004_attendanceupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='CanvasStatsUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.FileField(upload_to='canvasStats')),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('activated', models.BooleanField(default=False)),
            ],
        ),
    ]
