# Generated by Django 4.0.5 on 2022-08-02 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('B2CStaff', '0006_alter_kuryer_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kuryer_step',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_id', models.BigIntegerField()),
                ('step', models.BigIntegerField(blank=True, default=0)),
                ('obj', models.BigIntegerField(blank=True, default=0)),
            ],
        ),
    ]
