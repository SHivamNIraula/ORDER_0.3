# Generated by Django 4.2.7 on 2025-07-07 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tables', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='table',
            name='icon',
            field=models.ImageField(default='table_icons/default_table.jpg', upload_to='table_icons/'),
        ),
    ]
