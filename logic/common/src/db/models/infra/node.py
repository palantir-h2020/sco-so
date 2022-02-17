#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from ..auth.auth import Auth
from ..isolation.isolation_policy import IsolationPolicy
from mongoengine import BooleanField
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import StringField

import datetime


class Node(Document):
    """
    Node model
    """
    date = DateTimeField(default=datetime.datetime.now)
    host_name = StringField(required=True)
    ip_address = StringField(required=True)
    pcr0 = StringField(required=True)
    driver = StringField(required=True)
    analysis_type = StringField(required=True)
    distribution = StringField(required=True)
    isolated = BooleanField(default=False)
    terminated = BooleanField(default=False)
    authentication = ReferenceField(Auth, required=True)
    isolation_policy = ReferenceField(IsolationPolicy, required=True)
    termination_policy = ReferenceField(IsolationPolicy, required=True)
    disabled = BooleanField(required=True)
    physical = BooleanField(required=True)
    # Only needed in case node corresponds to VDUs
    instance_id = StringField(required=False)
    vnfr_id = StringField(required=False)
