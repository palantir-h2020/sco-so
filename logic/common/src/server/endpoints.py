#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


class SOEndpoints:

    ROOT = "/"
    # General resources
    NS = "{}ns".format(ROOT)
    XNF = "{}xnf".format(ROOT)
    INFRA = "{}infra".format(ROOT)
    TARGETS = "{}targets".format(ROOT)
    # General subentities
    INFRA_SVC = "{}/service".format(INFRA)
    LCM_ACT = "{}/action".format(NS)
    TARGETS_METRICS = "{}/metrics".format(TARGETS)
    # Modules
    LCM = "{}lcm".format(ROOT)
    MON = "{}mon".format(ROOT)
    PKG = "{}pkg".format(ROOT)
    # Endpoints
    LCM_NS = "{}/ns".format(LCM)
    LCM_NS_ACT = "{}/action".format(LCM_NS)
    LCM_XNF = "{}/xnf".format(LCM)
    MON_INFRA = "{}/infra".format(MON)
    MON_INFRA_SVC = "{}/service".format(MON_INFRA)
    MON_TARGETS = "{}/targets".format(MON)
    MON_TARGETS_METRICS = "{}/metrics".format(MON_TARGETS)
    PKG_NS = "{}/ns".format(PKG)
    PKG_XNF = "{}/xnf".format(PKG)
