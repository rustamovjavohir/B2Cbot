# Generated by Django 4.0.5 on 2022-07-29 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0009_b2cstep_is_safe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='b2corder',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата'),
        ),
    ]
