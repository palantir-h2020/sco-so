#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from enum import Enum


class HttpCode(Enum):

    """
    Compendium of HTTP codes.
    Details in https://httpstatuses.com
    """

    CONTINUE = 100
    SWITCH_PROTO = 101
    PROCESSING = 102

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTH_INFO = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226

    MULT_CHOICES = 300
    MOVED_PERM = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MOD = 304
    USE_PROXY = 305
    TEMP_RED = 307
    PERM_RED = 308

    BAD_REQUEST = 400
    UNAUTH = 401
    PAY_REQ = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METH_NOT_ALLOW = 405
    NOT_ACCEPT = 406
    PROXY_AUTH_REQ = 407
    REQ_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQ = 411
    PREC_FAILED = 412
    PAYLOAD_2_LARGE = 413
    URI_2_LONG = 414
    UNSUP_MEDIA = 415
    RANGE_NOT_SAT = 416
    EXP_FAILED = 417
    TEAPOT = 418
    MISDIR_REQ = 421
    UNPROC_ENT = 422
    LOCKED = 423
    FAILED_DEP = 424
    UPGRADE_REQ = 426
    PREC_REQ = 428
    TOO_MANY_REQ = 429
    RQ_HEAD_2_LARGE = 431
    CONN_WO_RESP = 444
    UNAV_4_LEGAL = 451
    CLI_CLOSED_REQ = 499

    INTERNAL_ERROR = 500
    NOT_IMPL = 501
    BAD_GW = 502
    SERV_UNAV = 503
    GW_TIMEOUT = 504
    HTTP_V_NOT_SUP = 505
    VAR_NEGOTIATE = 506
    INSUF_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    NET_AUTH_REQ = 511
    NET_CONN_TIMEOUT = 599

    def __get__(self, *args, **kwargs):
        return self.value

    def __str__(self):
        return str(self.value)

    @staticmethod
    def get(name):
        try:
            item = getattr(HttpCode, name)
            return getattr(item, "value")
        except AttributeError:
            return None
