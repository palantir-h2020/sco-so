#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.exception.exception import SOException
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from common.server.endpoints import VnsfoEndpoints as endpoints
from flask import Blueprint
from flask import request
from nfv.xnf import VnsfoVnsf
import json

so_views = Blueprint("so_xnf_views", __name__)


@so_views.route(endpoints.VNSF_C_VNSFS, methods=["GET"])
@so_views.route(endpoints.VNSF_C_VNSFS_R2, methods=["GET"])
def fetch_config_vnsfs():
    xnf_object = VnsfoVnsf()
    return HttpResponse.json(HttpCode.OK, xnf_object.get_xnfr_config())


@so_views.route(endpoints.VNSF_C_VNSFS_R4, methods=["GET"])
def fetch_config_vnsfs_r4():
    xnf_object = VnsfoVnsf(4)
    return HttpResponse.json(HttpCode.OK, xnf_object.get_xnfr_config())


@so_views.route(endpoints.VNSF_R_VNSFS, methods=["GET"])
@so_views.route(endpoints.VNSF_R_VNSFS_R2, methods=["GET"])
def fetch_running_vnsfs():
    xnf_object = VnsfoVnsf()
    return HttpResponse.json(HttpCode.OK, xnf_object.get_xnfr_running())


@so_views.route(endpoints.VNSF_R_VNSFS_R4, methods=["GET"])
def fetch_running_vnsfs_r4():
    xnf_object = VnsfoVnsf(4)
    return HttpResponse.json(HttpCode.OK, xnf_object.get_xnfr_running())


@so_views.route(endpoints.VNSF_VNSF_TENANT, methods=["GET"])
@so_views.route(endpoints.VNSF_VNSF_TENANT_R2, methods=["GET"])
def fetch_running_vnsfs_per_tenant(tenant_id):
    SOException.not_implemented()


@so_views.route(endpoints.VNSF_VNSF_TENANT_R4, methods=["GET"])
def fetch_running_vnsfs_per_tenant_r4(tenant_id):
    SOException.not_implemented()


@so_views.route(endpoints.VNSF_ACTION_EXEC, methods=["POST"])
@so_views.route(endpoints.VNSF_ACTION_EXEC_R2, methods=["POST"])
@content.expect_json_content
def exec_primitive_on_vnsf():
    xnf_object = VnsfoVnsf()
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    exp_params = ["vnsf_id", "action", "params"]
    if not content.data_in_request(
            request, exp_params):
        SOException.improper_usage(
                "Missing parameters: any of {}".format(exp_params))
    # Extract params, respecting the specific ordering
    payload = xnf_object.submit_action_request(
        *[request.json.get(x) for x in exp_params])
    try:
        payload_data = json.loads(payload)
    except json.decoder.JSONDecodeError:
        return HttpResponse.json(HttpCode.INTERNAL_ERROR,
                                 "{0} bad json".format(payload))
    if "statusCode" in payload_data:
        return HttpResponse.json(payload_data["statusCode"], payload)
    else:
        return HttpResponse.json(HttpCode.ACCEPTED, payload)


@so_views.route(endpoints.VNSF_ACTION_EXEC_R4, methods=["POST"])
@content.expect_json_content
def exec_primitive_on_vnsf_r4():
    xnf_object = VnsfoVnsf(4)
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    exp_params = ["vnsf_id", "action", "params"]
    if not content.data_in_request(
            request, exp_params):
        SOException.improper_usage(
                "Missing parameters: any of {}".format(exp_params))
    # Extract params, respecting the specific ordering
    payload = xnf_object.submit_action_request(
        *[request.json.get(x) for x in exp_params])
    try:
        payload_data = json.loads(payload)
    except json.decoder.JSONDecodeError:
        return HttpResponse.json(HttpCode.INTERNAL_ERROR,
                                 "{0} bad json".format(payload))
    if "statusCode" in payload_data:
        return HttpResponse.json(payload_data["statusCode"], payload)
    else:
        return HttpResponse.json(HttpCode.ACCEPTED, payload)
