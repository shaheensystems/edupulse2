# Generated by Django 4.2.6 on 2023-10-27 04:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0008_alter_staff_active_status_and_more'),
        ('program', '0006_rename_duration_in_month_course_duration_in_week_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='active_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='courseoffering',
            name='active_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='program',
            name='active_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='programoffering',
            name='active_status',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(choices=[('TV', 'tv'), ('IPAD', 'ipad'), ('PLAYSTATION', 'playstation')], max_length=11)),
                ('quantity', models.PositiveIntegerField()),
                ('total', models.FloatField(blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('salesman', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customUser.student')),
            ],
        ),
    ]
