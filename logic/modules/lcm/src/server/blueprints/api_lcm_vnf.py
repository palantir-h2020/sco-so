#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT

from common.exception import exception
from common.nfv.nfv.xnf import OSMInterfaceXNF
from common.server.endpoints import SOEndpoints
from flask import Blueprint, request

so_blueprints = Blueprint("so__lcm__xnf", __name__)


@so_blueprints.route(SOEndpoints.LCM_XNF, methods=["GET"])
@exception.handle_exc_resp
def list_xnf():
    _id = request.args.get("id")
    xnf_obj = OSMInterfaceXNF()
    return xnf_obj.get_xnfr_running(_id)
