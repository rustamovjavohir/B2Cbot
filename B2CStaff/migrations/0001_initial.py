# Generated by Django 4.0.5 on 2022-07-29 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Kuryer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kuryer_telegram_id', models.BigIntegerField(verbose_name='Курьер Telegram ID')),
                ('kuryer_name', models.CharField(blank=True, default='', max_length=100, verbose_name='Имя курьера')),
                ('kuryer_driver', models.BooleanField(default=False, verbose_name='ПВЗ')),
                ('kuryer_b2c', models.BooleanField(default=False, verbose_name='Б2С')),
                ('inwork', models.BooleanField(default=False, verbose_name='Работает?')),
                ('balance', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Курьер',
                'verbose_name_plural': 'Курьеры',
            },
        ),
    ]
