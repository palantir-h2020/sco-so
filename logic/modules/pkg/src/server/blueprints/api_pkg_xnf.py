#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.exception import exception
from common.nfv.nfv.xnf import OSMInterfaceXNF
from common.server.endpoints import SOEndpoints
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__xnf", __name__)


@so_blueprints.route(SOEndpoints.PKG_XNF, methods=["GET"])
@exception.handle_exc_resp
def list_pkg_xnf():
    _id = request.args.get("id")
    _name = request.args.get("name")
    xnf_obj = OSMInterfaceXNF()
    return xnf_obj.get_xnfr_config(_id, _name)


@so_blueprints.route(SOEndpoints.PKG_XNF, methods=["POST"])
@exception.handle_exc_resp
def upload_pkg_xnf():
    # Package is mandatory anyway, so it would never be None
    if request is not None and request.files is not None:
        _pkg_file = request.files.get("file")
    else:
        _pkg_file = None
    xnf_obj = OSMInterfaceXNF()
    return xnf_obj.onboard_package(_pkg_file)


@so_blueprints.route(SOEndpoints.PKG_XNF, methods=["DELETE"])
@exception.handle_exc_resp
def delete_pkg_xnf():
    _id = request.args.get("id")
    xnf_obj = OSMInterfaceXNF()
    return xnf_obj.delete_package(_id)
