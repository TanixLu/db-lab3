# Generated by Django 4.1a1 on 2022-05-30 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_branch_city_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='department',
            name='manager_id',
        ),
        migrations.AddField(
            model_name='staff',
            name='is_manager',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
