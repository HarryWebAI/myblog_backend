# Generated by Django 5.1.6 on 2025-03-31 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_alter_blog_title_alter_category_name_alter_tag_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'ordering': ['-is_top', '-created_at'], 'verbose_name': '博客', 'verbose_name_plural': '博客'},
        ),
        migrations.RemoveField(
            model_name='blog',
            name='published_at',
        ),
        migrations.RemoveField(
            model_name='blog',
            name='status',
        ),
    ]
