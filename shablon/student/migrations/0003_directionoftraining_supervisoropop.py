# Generated by Django 5.0 on 2024-04-29 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_alter_group_number_alter_group_title_student'),
        ('supervisorOPOP', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='directionoftraining',
            name='supervisorOPOP',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='supervisorOPOP.supervisoropop'),
        ),
    ]
