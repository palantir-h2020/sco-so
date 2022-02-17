#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, Document,\
    StringField


class PushgatewayResponse(Document):
    """
    Document storing the remote command response from the API
    """
    data = StringField()
    date = DateField()
    metric_command = StringField()
    metric_name = StringField()
    xnf_id = StringField()
    xnf_ip = StringField()
