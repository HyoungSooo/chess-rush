# Generated by Django 4.1.3 on 2023-05-20 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutomateFen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fen', models.CharField(max_length=40)),
                ('win', models.IntegerField(default=0)),
                ('draw', models.IntegerField(default=0)),
                ('loose', models.IntegerField(default=0)),
            ],
        ),
    ]
