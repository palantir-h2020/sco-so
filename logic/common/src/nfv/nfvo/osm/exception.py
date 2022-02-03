#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.exception.exception import SOException


class OSMUnknownPackageType(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = msg
        self.status_code = status_code


class OSMPackageNotFound(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = msg
        self.status_code = status_code


class OSMVNFKeyNotFound(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = "Private key to access VNF could not be found"
        if msg is not None:
            self.msg = "{0}. Details={1}".format(self.msg, msg)
        self.status_code = status_code


class OSMInstanceNotFound(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = "Running instance could not be found"
        if msg is not None:
            self.msg = "{0}. Details={1}".format(self.msg, msg)
        self.status_code = status_code


class OSMFailedInstantiation(SOException):
    def __init__(self, msg=None, status_code=409):
        self.msg = msg
        self.status_code = status_code


class OSMPackageConflict(SOException):
    def __init__(self, msg=None, status_code=409):
        self.msg = msg
        self.status_code = status_code


class OSMPackageError(SOException):
    """
    Understands Content-Type and request, but cannot process instructions.
    """
    def __init__(self, msg=None, status_code=422):
        self.msg = msg
        self.status_code = status_code


class OSMException(SOException):
    def __init__(self, msg=None, status_code=500):
        self.msg = msg
        self.status_code = status_code
