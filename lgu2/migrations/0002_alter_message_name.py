# Generated by Django 5.0.7 on 2024-08-16 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lgu2', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
