#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2017-present i2CAT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from common.exception.exception import SOException
from common.log.log import setup_custom_logger
from common.nfv.nfv.ns import VnsfoNs
from common.nfv.nfvo.osm.endpoints import NfvoEndpoints as endpoints
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
# from common.nfv.nfvo.osm.views.infra import check_auth_params
from flask import Blueprint
from flask import request

CONFIG_PATH = "../"
LOGGER = setup_custom_logger(__name__)
so_views = Blueprint("so_ns_views", __name__)
ns_object = VnsfoNs()


# Packages

@so_views.route(endpoints.NS_C_NSS, methods=["GET"])
def fetch_config_nss(instance_id=None):
    return HttpResponse.json(
        HttpCode.OK, ns_object.get_nsr_config(instance_id))


@so_views.route(endpoints.NS_C_NSS, methods=["POST"])
def upload_config_nss(ns_pkg_file):
    return HttpResponse.json(
        HttpCode.ACCEPTED, ns_object.onboard_package(ns_pkg_file))


@so_views.route(endpoints.NS_C_NSS, methods=["DELETE"])
def delete_config_nss(instance_id=None):
    return HttpResponse.json(
        HttpCode.ACCEPTED, ns_object.delete_package(instance_id))


# Running instances

def instantiate_ns_request_check():
    exp_ct = "application/json"
    # Request must have content to post
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    # Request must contain expected parameters
    exp_params = ["instance-name", "ns-name", "vim-id"]
    if not content.data_in_request(request, exp_params):
        SOException.improper_usage(
            "Missing parameters: any of {}"
            .format(exp_params))
    instantiation_data = request.get_json()
    return instantiation_data


@so_views.route(endpoints.NS_INSTANTIATE, methods=["POST"])
@content.expect_json_content
def instantiate_ns():
    try:
        instantiate_ns_request_check()
    except Exception as e:
        return HttpResponse.json(
            e.status_code, e.status_msg)
    result = ns_object.instantiate_ns(request.json)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)


@so_views.route(endpoints.NS_R_NSS, methods=["GET"])
@so_views.route(endpoints.NS_R_NSS_ID, methods=["GET"])
def fetch_running_nss(instance_id=None):
    nss = ns_object.get_nsr_running(instance_id)
    return HttpResponse.json(HttpCode.OK, nss)


@so_views.route(endpoints.NS_R_NSS)
@so_views.route(endpoints.NS_R_NSS_ID, methods=["DELETE"])
def delete_ns(instance_id=None):
    result = ns_object.delete_ns(instance_id)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)
