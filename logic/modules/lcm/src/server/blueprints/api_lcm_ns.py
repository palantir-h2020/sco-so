#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT

# from common.nfv.nfvo.osm.endpoints import NfvoEndpoints as endpoints
from common.nfv.nfvo.osm.views import ns, vnf
from common.server.http import content
from flask import Blueprint, request

so_blueprints = Blueprint("so__lcm__ns", __name__)


@so_blueprints.route("/lcm/ns", methods=["GET"])
def list_ns():
    _type = request.args.get("type")
    if _type == "available":
        return ns.fetch_config_nss()
    else:
        return ns.fetch_running_nss()


@so_blueprints.route("/lcm/ns/<ns_id>", methods=["GET"])
def list_ns_by_id(ns_id=None):
    _type = request.args.get("type")
    if _type == "available":
        return ns.fetch_config_nss(ns_id)
    else:
        return ns.fetch_running_nss(ns_id)


# TODO FIXME
@so_blueprints.route("/lcm/ns", methods=["POST"])
@content.expect_json_content
def instantiate_ns():
    return ns.instantiate_ns()


# TODO TEST
@so_blueprints.route("/lcm/ns/<ns_id>", methods=["DELETE"])
def delete_ns(ns_id=None):
    return ns.delete_ns(ns_id)


@so_blueprints.route("/lcm/vnf", methods=["GET"])
def list_vnf():
    _type = request.args.get("type")
    # Packages # TODO: move to PKG
    if _type == "available":
        return vnf.fetch_config_vnfs()
    # Instances
    else:
        return vnf.fetch_running_vnfs()


@so_blueprints.route("/lcm/vnf/<vnf_id>", methods=["GET"])
def list_vnf_by_id(vnf_id=None):
    _type = request.args.get("type")
    if _type == "available":
        return vnf.fetch_config_vnfs(vnf_id)
    else:
        return vnf.fetch_running_vnfs(vnf_id)
