# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0010_auto_20150510_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='notAfter',
            field=models.DateTimeField(null=True, verbose_name='Not After', blank=True),
        ),
        migrations.AddField(
            model_name='host',
            name='notBefore',
            field=models.DateTimeField(null=True, verbose_name='Not Before', blank=True),
        ),
    ]
