# Generated by Django 5.0.6 on 2025-04-10 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking_api', '0003_alter_room_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ['room_number']},
        ),
    ]
