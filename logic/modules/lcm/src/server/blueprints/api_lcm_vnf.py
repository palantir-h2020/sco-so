#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT

from common.exception import exception
from common.nfv.nfv.vnf import OSMInterfaceVNF
from common.server.endpoints import SOEndpoints
from flask import Blueprint, request

so_blueprints = Blueprint("so__lcm__vnf", __name__)


@so_blueprints.route(SOEndpoints.LCM_VNF, methods=["GET"])
@exception.handle_exc_resp
def list_vnf():
    _id = request.args.get("id")
    vnf_obj = OSMInterfaceVNF()
    return vnf_obj.get_vnfr_running(_id)
