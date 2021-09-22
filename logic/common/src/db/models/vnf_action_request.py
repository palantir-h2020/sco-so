#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from mongoengine import DateTimeField
from mongoengine import DictField
from mongoengine import Document
from mongoengine import StringField

import datetime


class VnfActionRequest(Document):
    """
    Vnf action request model
    """
    date = DateTimeField(default=datetime.datetime.now)
    primitive = StringField(required=True)
    params = DictField()
    vnsfr_id = StringField()
    response = DictField()
