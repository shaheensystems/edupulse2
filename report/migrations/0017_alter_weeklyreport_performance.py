# Generated by Django 4.2.6 on 2023-12-04 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0016_alter_weeklyreport_performance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyreport',
            name='performance',
            field=models.CharField(blank=True, choices=[('na', 'N/A'), ('poor', 'POOR'), ('good', 'GOOD'), ('moderate', 'MODERATE')], default='n/a', max_length=255, null=True),
        ),
    ]
