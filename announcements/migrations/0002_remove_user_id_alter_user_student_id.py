# Generated by Django 5.2 on 2025-05-01 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='id',
        ),
        migrations.AlterField(
            model_name='user',
            name='student_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
