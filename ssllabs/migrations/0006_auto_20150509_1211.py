# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0005_auto_20150509_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='endTime',
            field=models.DateTimeField(null=True, verbose_name='End Time'),
        ),
        migrations.AlterField(
            model_name='host',
            name='startTime',
            field=models.DateTimeField(null=True, verbose_name='Start Time'),
        ),
    ]
