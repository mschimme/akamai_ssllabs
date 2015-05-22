# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('host_id', models.AutoField(primary_key=True, serialize=False)),
                ('host', models.CharField(unique=True, max_length=100)),
                ('port', models.IntegerField(default=443)),
                ('status', models.CharField(max_length=20)),
                ('statusMessage', models.CharField(max_length=100)),
                ('startTime', models.DateTimeField(verbose_name='Start Time')),
                ('endTime', models.DateTimeField(verbose_name='End Time')),
                ('ipAddress', models.CharField(max_length=20)),
                ('grade', models.CharField(max_length=3)),
                ('gradeTrustIgnored', models.CharField(max_length=3)),
                ('account_id', models.ForeignKey(to='ssllabs.Account')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('profileId', models.AutoField(primary_key=True, serialize=False)),
                ('profileName', models.CharField(unique=True, max_length=20)),
                ('lastModified', models.DateTimeField(verbose_name='Last Modified')),
            ],
        ),
        migrations.CreateModel(
            name='ProfileHosts',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('host', models.ForeignKey(to='ssllabs.Host')),
                ('profileId', models.ForeignKey(to='ssllabs.Profile')),
            ],
        ),
    ]
