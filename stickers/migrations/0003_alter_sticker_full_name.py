# Generated by Django 4.0.2 on 2022-03-26 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stickers', '0002_alter_sticker_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sticker',
            name='full_name',
            field=models.CharField(default=' ', max_length=50),
        ),
    ]
