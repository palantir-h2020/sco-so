#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import StringField

import datetime


class SdnController(Document):
    """
    SdnController (ODL) model
    """
    date = DateTimeField(default=datetime.datetime.now)
    name = StringField(required=True)
