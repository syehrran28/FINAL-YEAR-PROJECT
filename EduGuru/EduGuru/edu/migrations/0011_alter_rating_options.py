# Generated by Django 5.1.2 on 2024-12-13 01:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0010_alter_tutorprofile_school_level'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rating',
            options={'ordering': ['-created_at']},
        ),
    ]
