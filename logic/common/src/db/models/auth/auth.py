#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from mongoengine import DateTimeField
from mongoengine import Document
from mongoengine import StringField

import datetime


class Auth(Document):
    """
    Auth model
    """
    date = DateTimeField(default=datetime.datetime.now)
    username = StringField(required=True)
    meta = {"allow-inheritance": True, "abstract": True}


class KeyAuth(Auth):
    """
    KeyAuth model
    """
    private_key = StringField(required=True)


class PasswordAuth(Auth):
    """
    PasswordAuth model
    """
    password = StringField(required=True)
