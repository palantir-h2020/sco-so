#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.exception import exception
from common.nfv.nfv.ns import OSMInterfaceNS
from common.server.endpoints import SOEndpoints
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__ns", __name__)


@so_blueprints.route(SOEndpoints.PKG_NS, methods=["GET"])
@exception.handle_exc_resp
def list_pkg_ns():
    _id = request.args.get("id")
    _name = request.args.get("name")
    ns_obj = OSMInterfaceNS()
    return ns_obj.get_nsr_config(_id, _name)


@so_blueprints.route(SOEndpoints.PKG_NS, methods=["POST"])
@exception.handle_exc_resp
def upload_pkg_ns():
    _pkg_file = request.files["file"]
    ns_obj = OSMInterfaceNS()
    return ns_obj.onboard_package(_pkg_file)


@so_blueprints.route(SOEndpoints.PKG_NS, methods=["DELETE"])
@exception.handle_exc_resp
def delete_pkg_ns():
    _id = request.args.get("id")
    ns_obj = OSMInterfaceNS()
    return ns_obj.delete_package(_id)
