#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateField, Document,\
    StringField


class RemoteCommand(Document):
    """
    Document storing the remote command from the user and
    keep accountancy on their modifications.
    """
    xnf_id = StringField()
    metric_name = StringField()
    metric_command = StringField()
    data = StringField()
    date = DateField()
