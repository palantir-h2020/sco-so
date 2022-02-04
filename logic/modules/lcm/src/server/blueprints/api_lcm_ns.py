#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT

from common.nfv.nfvo.osm.views import ns
from common.server.http import content
from flask import Blueprint, request

so_blueprints = Blueprint("so__lcm__ns", __name__)


@so_blueprints.route("/lcm/ns", methods=["GET"])
def list_ns():
    _id = request.args.get("id")
    return ns.fetch_running_nss(_id)


# TODO FIXME
@so_blueprints.route("/lcm/ns", methods=["POST"])
@content.expect_json_content
def instantiate_ns():
    return ns.instantiate_ns()


# TODO TEST
@so_blueprints.route("/lcm/ns/<ns_id>", methods=["DELETE"])
def delete_ns(ns_id=None):
    return ns.delete_ns(ns_id)
