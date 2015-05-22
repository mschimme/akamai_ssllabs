# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0007_auto_20150509_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='status',
            field=models.CharField(null=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='host',
            name='statusMessage',
            field=models.CharField(null=True, max_length=100),
        ),
    ]
