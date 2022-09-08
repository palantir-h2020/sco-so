#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, Document,\
    StringField

class PushgatewayRequest(Document):
    """
    Document storing the remote command request from the user
    """
    vnf_id = StringField()
    vnf_ip = StringField()
    metric_name = StringField()
    metric_command = StringField()
    date = DateField()