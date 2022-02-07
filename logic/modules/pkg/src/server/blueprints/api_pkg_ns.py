#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.nfv.nfv.ns import VnsfoNs
# TODO: remove the views' level of indirection in all methods
from common.nfv.nfvo.osm.views import ns
from common.server.http.http_response import HttpResponse
from common.utils.osm_response_parsing import OSMResponseParsing
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__ns", __name__)
ns_obj = VnsfoNs()


@so_blueprints.route("/pkg/ns", methods=["GET"])
def list_pkg_ns():
    _id = request.args.get("id")
    _name = request.args.get("name")
    filter = _id
    if filter is None:
        filter = _name
    return ns.fetch_config_nss(filter)


@so_blueprints.route("/pkg/ns", methods=["POST"])
def upload_pkg_ns():
    ns_pkg_file = request.files["file"]
    # ns_pkg_contents = ns_pkg_file.read()
    ns_pkg_contents = ns_pkg_file
    # TODO: same as here, remove the views' level
    # of indirection in all methods
    # return ns.upload_config_ns(ns_pkg_contents)
    return ns_obj.onboard_package(ns_pkg_contents)


@so_blueprints.route("/pkg/ns", methods=["DELETE"])
def delete_pkg_ns():
    _id = request.args.get("id")
    content_type = request.environ.get("HTTP_ACCEPT")
    try:
        result = ns.delete_config_nss(_id)
        parsed_result = OSMResponseParsing.parse_generic(result, content_type)
        if "internal-error" not in parsed_result.keys():
            return HttpResponse.infer({
                "output": parsed_result.get("response")},
                parsed_result.get("status-code"))
        else:
            return HttpResponse.infer({
                "output": parsed_result.get("response"),
                "internal-error": parsed_result.get("internal-error")},
                parsed_result.get("status-code"))
    except Exception as e:
        exc_data = OSMResponseParsing.parse_exception(e)
        return HttpResponse.infer({
            "output": exc_data.get("detail")},
            exc_data.get("status"), content_type)
