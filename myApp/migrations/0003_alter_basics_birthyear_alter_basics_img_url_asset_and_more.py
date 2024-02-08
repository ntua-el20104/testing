# Generated by Django 5.0.1 on 2024-02-03 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0002_basics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basics',
            name='birthYear',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='basics',
            name='img_url_asset',
            field=models.URLField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='basics',
            name='knownForTitles',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='basics',
            name='primaryProfession',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
