#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, Document,\
    StringField

class CustomMetrics(Document):
    """
    Document storing the remote command from the user and
    keep accountancy on their modifications.
    """
    data = StringField()
    date = DateField()
    metric_command = StringField()
    metric_name = StringField()
    vnf_id = StringField()
    
    
    
    