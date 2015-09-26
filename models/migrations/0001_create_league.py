# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.CharField(primary_key=True, serialize=False, max_length=200)),
                ('name', models.TextField()),
            ],
        ),
    ]
