#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import StringField

import datetime


class IsolationRecord(Document):
    """
    Isolation record
    """
    date = DateTimeField(default=datetime.datetime.now)
    output = StringField(required=True)
    error = StringField(required=True)
