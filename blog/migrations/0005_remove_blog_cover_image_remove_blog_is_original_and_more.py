# Generated by Django 5.1.6 on 2025-03-30 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_alter_comment_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blog',
            name='cover_image',
        ),
        migrations.RemoveField(
            model_name='blog',
            name='is_original',
        ),
        migrations.RemoveField(
            model_name='blog',
            name='original_url',
        ),
        migrations.RemoveField(
            model_name='blog',
            name='slug',
        ),
    ]
