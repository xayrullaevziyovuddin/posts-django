# Generated by Django 5.1 on 2024-08-26 15:39

import markdownx.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0004_alter_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='body',
            field=markdownx.models.MarkdownxField(),
        ),
    ]
