#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from mongoengine import DateTimeField
from mongoengine import DictField
from mongoengine import Document
from mongoengine import StringField
import datetime


class XnfActionRequest(Document):
    """
    xNF action request model
    """
    date = DateTimeField(default=datetime.datetime.now)
    primitive = StringField(required=True)
    params = DictField()
    vnsfr_id = StringField()
    response = DictField()
