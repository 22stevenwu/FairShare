# Generated by Django 5.1.4 on 2025-01-09 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_remove_bill_total_owed_remove_bill_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='is_current',
            field=models.BooleanField(default=True),
        ),
    ]
