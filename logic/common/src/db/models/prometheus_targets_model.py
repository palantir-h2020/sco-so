#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, DictField, Document, EmbeddedDocumentField, ListField, StringField
from prometheus_targets_operation import PrometheusTargetsOperation

class PrometheusTargets(Document):
    """
    Document storing the Prometheus targets and
    keep accountancy on their modifications.
    """
    targets = ListField(StringField())
    date = DateField()
    modification = DictField(EmbeddedDocumentField(PrometheusTargetsOperation))

