# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='signatureAlg',
            field=models.CharField(default='SHA256withRSA', max_length=20),
            preserve_default=False,
        ),
    ]
