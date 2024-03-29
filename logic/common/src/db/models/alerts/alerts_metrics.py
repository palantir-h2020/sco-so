#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import Document, DateField, StringField

class AlertsMetrics(Document):
    """
    Document storing an alert with associated metric
    """
    xnf_id = StringField()
    metric_name = StringField()
    metric_command = StringField()
    data = StringField()
    date = DateField()