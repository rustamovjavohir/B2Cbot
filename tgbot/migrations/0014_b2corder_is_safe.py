# Generated by Django 4.0.5 on 2022-08-01 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0013_b2cprice_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='b2corder',
            name='is_safe',
            field=models.BooleanField(default=False, verbose_name='Тип доставка'),
        ),
    ]
