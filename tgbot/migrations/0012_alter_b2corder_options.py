# Generated by Django 4.0.5 on 2022-08-01 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0011_b2corder_kuryer'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='b2corder',
            options={'ordering': ['-id'], 'verbose_name': 'Б2С Заказ', 'verbose_name_plural': 'Б2С Заказы'},
        ),
    ]
