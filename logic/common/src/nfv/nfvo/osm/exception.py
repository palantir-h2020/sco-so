#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.exception.exception import SOException
from common.server.http.http_code import HttpCode


class OSMException(Exception):
    def __init__(self, msg=None, status_code=HttpCode.INTERNAL_ERROR):
        if msg is None or len(msg) == 0:
            msg = {}
        if "error" not in msg.keys():
            msg.update({"error": "Internal error"})
        if "status" not in msg.keys():
            msg.update({"status": HttpCode.INTERNAL_ERROR})
        self.msg = msg
        if status_code is None:
            self.status_code = msg.get("status")
        else:
            self.status_code = status_code


class OSMUnknownPackageType(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = msg
        self.status_code = status_code


class OSMPackageNotFound(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = msg
        self.status_code = status_code


class OSMXNFKeyNotFound(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = "Private key to access xNF could not be found"
        if msg is not None:
            self.msg = msg
        self.status_code = status_code


class OSMInstanceNotFound(SOException):
    def __init__(self, msg=None, status_code=404):
        self.msg = "Running instance could not be found"
        if msg is not None:
            self.msg = msg
        self.status_code = status_code


class OSMResourceNotFound(OSMException):
    def __init__(self, msg={}, status_code=HttpCode.NOT_FOUND):
        super().__init__(msg, status_code)
        if "error" not in msg.keys():
            self.msg.update({"error": "Resource not found"})
        self.msg.update({"status": HttpCode.NOT_FOUND})
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


class OSMInstanceConflict(SOException):
    def __init__(self, msg=None, status_code=409):
        self.msg = msg
        self.status_code = status_code


class OSMException(SOException):
    def __init__(self, msg=None, status_code=500):
        self.msg = msg
        self.status_code = status_code
