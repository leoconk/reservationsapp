# Generated by Django 5.2.2 on 2025-06-12 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='name',
            field=models.CharField(default='Anonymous', max_length=100),
            preserve_default=False,
        ),
    ]
