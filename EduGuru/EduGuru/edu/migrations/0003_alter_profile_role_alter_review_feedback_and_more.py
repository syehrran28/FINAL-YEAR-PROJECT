# Generated by Django 5.1.2 on 2024-12-05 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edu', '0002_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(blank=True, choices=[('parent_student', 'Parent/Student'), ('tutor_center', 'Tutor/Tuition Center')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='tutorprofile',
            name='teaching_experience',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
