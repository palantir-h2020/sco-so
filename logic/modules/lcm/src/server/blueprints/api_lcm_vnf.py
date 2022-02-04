#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT

from common.nfv.nfvo.osm.views import vnf
from flask import Blueprint, request

so_blueprints = Blueprint("so__lcm__vnf", __name__)


@so_blueprints.route("/lcm/vnf", methods=["GET"])
def list_vnf():
    _id = request.args.get("id")
    return vnf.fetch_running_vnfs(_id)
