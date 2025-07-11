# Generated by Django 5.1.2 on 2024-12-12 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0008_tutorprofile_youtube_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorprofile',
            name='school_level',
            field=models.CharField(blank=True, choices=[('kindergarten', 'Kindergarten (4 to 6 years)'), ('primary', 'Primary School (Standard 1 to Standard 6)'), ('secondary', 'Secondary School (Form 1 to Form 5)'), ('preuniversity', 'Pre-University (STPM/Foundation/A-Levels)'), ('university', 'University/College')], max_length=20, null=True),
        ),
    ]
