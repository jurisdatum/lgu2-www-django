# Generated by Django 5.1.4 on 2025-01-16 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lgu2', '0003_alter_footer_copyright_statement_cy_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='footer',
            name='eur_lex_link',
        ),
        migrations.RemoveField(
            model_name='footer',
            name='logo_image',
        ),
        migrations.RemoveField(
            model_name='footer',
            name='open_government_licence_link',
        ),
    ]
