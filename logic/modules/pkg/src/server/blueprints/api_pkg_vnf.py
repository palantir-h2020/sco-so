#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.exception import exception
from common.nfv.nfv.vnf import OSMInterfaceVNF
from common.server.endpoints import SOEndpoints
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__vnf", __name__)


@so_blueprints.route(SOEndpoints.PKG_VNF, methods=["GET"])
@exception.handle_exc_resp
def list_pkg_vnf():
    _id = request.args.get("id")
    _name = request.args.get("name")
    vnf_obj = OSMInterfaceVNF()
    return vnf_obj.get_vnfr_config(_id, _name)


@so_blueprints.route(SOEndpoints.PKG_VNF, methods=["POST"])
@exception.handle_exc_resp
def upload_pkg_vnf():
    _pkg_file = request.files["file"]
    vnf_obj = OSMInterfaceVNF()
    return vnf_obj.onboard_package(_pkg_file)


@so_blueprints.route(SOEndpoints.PKG_VNF, methods=["DELETE"])
@exception.handle_exc_resp
def delete_pkg_vnf():
    _id = request.args.get("id")
    vnf_obj = OSMInterfaceVNF()
    return vnf_obj.delete_package(_id)
