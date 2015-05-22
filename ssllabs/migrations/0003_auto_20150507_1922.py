# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0002_host_signaturealg'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='supportsRC4',
            field=models.CharField(choices=[('Y', 'Yes'), ('N', 'No'), ('NA', 'NA')], default='NA', max_length=3),
        ),
        migrations.AlterField(
            model_name='host',
            name='ipAddress',
            field=models.GenericIPAddressField(),
        ),
    ]
