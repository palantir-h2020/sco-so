#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


class SOEndpoints:

    ROOT = "/"
    # General resources
    NS = "{}ns".format(ROOT)
    VNF = "{}vnf".format(ROOT)
    INFRA = "{}infra".format(ROOT)
    # General subresources
    INFRA_SVC = "{}/service".format(INFRA)
    # Modules
    LCM = "{}lcm".format(ROOT)
    MON = "{}mon".format(ROOT)
    PKG = "{}pkg".format(ROOT)
    # Endpoints
    LCM_NS = "{}/ns".format(LCM)
    LCM_VNF = "{}/vnf".format(LCM)
    MON_INFRA = "{}/infra".format(MON)
    MON_INFRA_SVC = "{}/service".format(MON_INFRA)
    PKG_NS = "{}/ns".format(PKG)
    PKG_VNF = "{}/vnf".format(PKG)
