#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, Document,\
    StringField

class PushgatewayResponse(Document):
    """
    Document storing the remote command response from the API
    """
    vnf_id = StringField()
    vnf_ip = StringField()
    metric_name = StringField()
    metric_command = StringField()
    data = StringField()
    date = DateField()