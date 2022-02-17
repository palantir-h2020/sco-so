#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from ..auth.auth import Auth
from ..isolation.isolation_polict import IsolationPolicy
from ..network.sdn_controller import SDNController
from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import StringField

import datetime


class Switch(Document):
    """
    Switch model
    """
    date = DateTimeField(default=datetime.datetime.now)
    name = StringField(required=True)
    authentication = Auth(required=True)
    isolation_policy = IsolationPolicy(required=True)
    ip_address = StringField(required=True)
    virtual = BooleanField(required=True)
    sdn_controller = ReferenceField(SDNController)
