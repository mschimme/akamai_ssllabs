# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0003_auto_20150507_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='supportsRC4',
            field=models.CharField(max_length=4),
        ),
    ]
