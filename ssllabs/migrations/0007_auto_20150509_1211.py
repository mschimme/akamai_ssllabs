# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ssllabs', '0006_auto_20150509_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='grade',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='gradeTrustIgnored',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='ipAddress',
            field=models.GenericIPAddressField(null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='signatureAlg',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='host',
            name='supportsRC4',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
