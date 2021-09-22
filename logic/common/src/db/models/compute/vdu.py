#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from ..auth.auth import Auth
from ..infra.node import Node
from ..isolation.isolation_policy import IsolationPolicy
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import StringField

import datetime


class Vdu(Document):
    """
    Vdu model
    """
    date = DateTimeField(default=datetime.datetime.now)
    name = StringField(required=True)
    management_ip = StringField(required=True)
    authentication = ReferenceField(Auth, required=True)
    isolation_policy = ReferenceField(IsolationPolicy, required=True)
    node = ReferenceField(Node, required=True)
