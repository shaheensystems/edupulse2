# Generated by Django 4.2.6 on 2023-10-29 06:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0008_delete_sale'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='courseoffering',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='program',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='programoffering',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
