# Generated by Django 5.2 on 2025-05-04 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements', '0004_alter_announcement_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='student_id',
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
    ]
