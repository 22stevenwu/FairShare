# Generated by Django 5.1.4 on 2025-01-08 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_billsplit_amount_owed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='billsplit',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
