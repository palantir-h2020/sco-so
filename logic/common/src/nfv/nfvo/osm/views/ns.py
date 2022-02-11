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
from common.nfv.nfv.ns import OSMInterfaceNS
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
# from common.nfv.nfvo.osm.views.infra import check_auth_params
from flask import Blueprint
from flask import request

CONFIG_PATH = "../"
LOGGER = setup_custom_logger(__name__)
so_views = Blueprint("so_ns_views", __name__)
ns_object = OSMInterfaceNS()


# TODO REMOVE

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
