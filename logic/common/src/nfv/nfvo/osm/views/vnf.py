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
from common.nfv.nfv.vnf import VnsfoVnsf
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from common.nfv.nfvo.osm.endpoints import NfvoEndpoints as endpoints
from flask import Blueprint
from flask import request
import json

so_views = Blueprint("so_vnf_views", __name__)


@so_views.route(endpoints.VNSF_C_VNSFS, methods=["GET"])
def fetch_config_vnfs(instance_id=None):
    vnf_object = VnsfoVnsf()
    return HttpResponse.json(
        HttpCode.OK, vnf_object.get_vnfr_config(instance_id))


@so_views.route(endpoints.VNSF_R_VNSFS, methods=["GET"])
def fetch_running_vnfs(instance_id=None):
    vnf_object = VnsfoVnsf()
    return HttpResponse.json(
        HttpCode.OK, vnf_object.get_vnfr_running(instance_id))


@so_views.route(endpoints.VNSF_VNSF_TENANT, methods=["GET"])
def fetch_running_vnfs_per_tenant(tenant_id):
    SOException.not_implemented()


@so_views.route(endpoints.VNSF_ACTION_EXEC, methods=["POST"])
@content.expect_json_content
def exec_primitive_on_vnsf():
    vnf_object = VnsfoVnsf()
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    exp_params = ["vnf-id", "action", "params"]
    if not content.data_in_request(
            request, exp_params):
        SOException.improper_usage(
                "Missing parameters: any of {}".format(exp_params))
    # Extract params, respecting the specific ordering
    payload = vnf_object.submit_action_request(
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
