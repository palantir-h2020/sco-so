#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from .isolation_record import IsolationRecord
from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import ListField
from mongoengine import ReferenceField
from mongoengine import StringField

import datetime


class IsolationPolicy(Document):
    """
    Isolation policy abstract base class
    """
    date = DateTimeField(default=datetime.datetime.now)
    name = StringField(required=True)
    records = ListField(ReferenceField(IsolationRecord))
    meta = {"allow-inheritance": True, "abstract": True}


class InterfaceDown(IsolationPolicy):
    """
    Isolation policy (set down an interface)
    """
    interface_name = StringField(required=True)


class DeleteFlow(IsolationPolicy):
    """
    Isolation policy (delete flow from controller)
    """
    switch = StringField()
    target_filter = StringField()


class Shutdown(IsolationPolicy):
    """
    Consisting on shutting down the resource
    """
    command = StringField(required=True)


class OpenstackIsolation(IsolationPolicy):
    """
    Consisting on removing vdu ports
    """
    identity_endpoint = StringField()
    username = StringField()
    password = StringField()
    project_name = StringField()
    domain_name = StringField()


class OpenstackTermination(IsolationPolicy):
    """
    Consisting on shutting down the vdu
    """
    identity_endpoint = StringField()
    username = StringField()
    password = StringField()
    project_name = StringField()
    domain_name = StringField()
