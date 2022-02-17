#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, Document,\
    EmbeddedDocumentField, ListField, StringField
from common.db.models.prometheus_targets_operation\
    import PrometheusTargetsOperation


class PrometheusTargets(Document):
    """
    Document storing the Prometheus targets and
    keep accountancy on their modifications.
    """
    targets = ListField(StringField())
    date = DateField()
    modification = EmbeddedDocumentField(PrometheusTargetsOperation)
