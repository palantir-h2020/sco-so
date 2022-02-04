#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.nfv.nfvo.osm.views import vnf
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__vnf", __name__)


@so_blueprints.route("/pkg/vnf", methods=["GET"])
def list_pkg_vnf():
    _id = request.args.get("id")
    return vnf.fetch_config_vnfs(_id)
