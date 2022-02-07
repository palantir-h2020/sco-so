#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.nfv.nfv.vnf import VnsfoVnsf
# TODO: remove the views' level of indirection in all methods
from common.nfv.nfvo.osm.views import vnf
from common.server.http.http_response import HttpResponse
from common.utils.osm_response_parsing import OSMResponseParsing
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__vnf", __name__)
vnf_obj = VnsfoVnsf()


@so_blueprints.route("/pkg/vnf", methods=["GET"])
def list_pkg_vnf():
    _id = request.args.get("id")
    _name = request.args.get("name")
    filter = _id
    if filter is None:
        filter = _name
    return vnf.fetch_config_vnfs(filter)


@so_blueprints.route("/pkg/vnf", methods=["POST"])
def upload_pkg_vnf():
    vnf_pkg_file = request.files["file"]
    # vnf_pkg_contents = vnf_pkg_file.read()
    vnf_pkg_contents = vnf_pkg_file
    # TODO: same as here, remove the views' level
    # of indirection in all methods
    # return vnf.upload_config_vnf(vnf_pkg_contents)
    return vnf_obj.onboard_package(vnf_pkg_contents)


@so_blueprints.route("/pkg/vnf", methods=["DELETE"])
def delete_pkg_vnf():
    _id = request.args.get("id")
    content_type = request.environ.get("HTTP_ACCEPT")
    try:
        result = vnf.delete_config_vnf(_id)
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
