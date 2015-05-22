# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0008_auto_20150509_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='endTime',
            field=models.DateTimeField(blank=True, verbose_name='End Time', null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='startTime',
            field=models.DateTimeField(blank=True, verbose_name='Start Time', null=True),
        ),
    ]
