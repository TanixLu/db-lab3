# Generated by Django 4.1a1 on 2022-05-30 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_department_manager_id_staff_is_manager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkingaccount',
            name='branch_name',
        ),
        migrations.RemoveField(
            model_name='savingaccount',
            name='branch_name',
        ),
    ]