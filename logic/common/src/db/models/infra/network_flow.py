#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import IntField
from mongoengine import StringField

import datetime


class NetworkFlow(Document):
    """
    Network flow model
    """
    date = DateTimeField(default=datetime.datetime.now)
    device_id = StringField(required=True)
    table_id = IntField(required=True)
    flow_id = StringField(required=True)
    flow = StringField(required=True)
    trusted = BooleanField(default=False, required=True)
