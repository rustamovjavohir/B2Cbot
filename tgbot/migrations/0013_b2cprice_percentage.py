# Generated by Django 4.0.5 on 2022-08-01 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0012_alter_b2corder_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='b2cprice',
            name='percentage',
            field=models.IntegerField(blank=True, null=True, verbose_name='Процент (%)'),
        ),
    ]
