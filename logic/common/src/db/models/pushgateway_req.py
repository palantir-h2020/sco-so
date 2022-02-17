#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, Document,\
    StringField


class PushgatewayRequest(Document):
    """
    Document storing the remote command request from the user
    """
    date = DateField()
    metric_command = StringField()
    metric_name = StringField()
    vnf_id = StringField()
    vnf_ip = StringField()
