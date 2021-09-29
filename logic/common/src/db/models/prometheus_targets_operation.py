#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import EmbeddedDocument, StringField

class PrometheusTargetsOperation(EmbeddedDocument):
    """
    Document to save targets operations add, modify, delete
    """
    operation = StringField()
    current_target = StringField()
    new_target = StringField()

