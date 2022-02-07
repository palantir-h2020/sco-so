#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT

from common.nfv.nfvo.osm.views import ns
from common.server.http.http_response import HttpResponse
from common.utils.osm_response_parsing import OSMResponseParsing
from flask import Blueprint, request

so_blueprints = Blueprint("so__pkg__ns", __name__)


@so_blueprints.route("/pkg/ns", methods=["GET"])
def list_pkg_ns():
    _id = request.args.get("id")
    return ns.fetch_config_nss(_id)


@so_blueprints.route("/pkg/ns", methods=["POST"])
def upload_pkg_ns():
    ns_pkg_file = request.files["file"].read()
    return ns.upload_config_nss(ns_pkg_file)


@so_blueprints.route("/pkg/ns", methods=["DELETE"])
def delete_pkg_ns():
    _id = request.args.get("id")
    content_type = request.environ.get("HTTP_ACCEPT")
    try:
        result = ns.delete_config_ns(_id)
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
