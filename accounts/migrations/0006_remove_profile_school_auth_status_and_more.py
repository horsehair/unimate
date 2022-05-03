# Generated by Django 4.0.2 on 2022-04-26 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_rename_agree_user_information_agree_user_use_agree_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='school_auth_status',
        ),
        migrations.AddField(
            model_name='profile',
            name='auth_status',
            field=models.CharField(choices=[('Registered', 'Registered - Should Enter Profile '), ('Profile complete', 'Profile complete - Should Authenticate School'), ('School complete', 'School Authentication Complete')], default='Registered', max_length=80),
        ),
    ]
