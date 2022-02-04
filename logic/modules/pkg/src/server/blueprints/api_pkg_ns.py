#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.nfv.nfvo.osm.views import ns
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__ns", __name__)


@so_blueprints.route("/pkg/ns", methods=["GET"])
def list_pkg_ns():
    _id = request.args.get("id")
    return ns.fetch_config_nss(_id)
