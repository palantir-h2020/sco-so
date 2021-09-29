#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import EmbeddedDocument, StringField, DateField, DictField, Document, EmbeddedDocumentField, ListField

class PrometheusTargetsOperation(EmbeddedDocument):
    """
    Document to save targets operations add, modify, delete
    """
    operation = StringField()
    current_target = StringField()
    new_target = StringField()

class PrometheusTargets(Document):
    """
    Document storing the Prometheus targets and
    keep accountancy on their modifications.
    """
    targets = ListField(StringField())
    date = DateField()
    modification = DictField(EmbeddedDocumentField(PrometheusTargetsOperation))
