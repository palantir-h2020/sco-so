#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import Document, DateField, StringField, IntField

class AlertRegister(Document):
    """
    Document storing an Alert Registration
    """
    alert_name = StringField()
    date = DateField()
    operator = StringField()
    hook_endpoint = StringField()
    hook_type = StringField()
    threshold = IntField()
    time_validity = IntField()
   
    
    