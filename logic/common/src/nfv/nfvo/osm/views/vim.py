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
from common.nfv.nfvi.vim import VnsfoVim as vim_s
from common.nfv.nfvo.osm.endpoints import NfvoEndpoints as endpoints
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint
from flask import request

so_views = Blueprint("so_vim_views", __name__)
so_vnf = vim_s()


@so_views.route(endpoints.VIM_LIST, methods=["GET"])
@content.expect_json_content
def get_vim_list():
    return HttpResponse.json(HttpCode.OK, so_vnf.get_vim_list())


@so_views.route(endpoints.VIM_IMAGE, methods=["GET"])
@content.expect_json_content
def get_vim_images():
    return HttpResponse.json(HttpCode.OK, so_vnf.get_vim_img_list())


@so_views.route(endpoints.VIM_IMAGE_UPLOAD, methods=["POST"])
@content.expect_json_content
def register_vnf_image(vim_id):
    exp_ct = "multipart/form-data"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    if not(len(request.files) > 0 and "image" in request.files.keys()):
        SOException.improper_usage("Missing file")
    img_bin = request.files.get("image")
    img_name = img_bin.filename
    # img_name = img_name[0:img_name.index(".")-1]
    output = so_vnf.register_vdu(vim_id, img_name, img_bin.stream)
    return HttpResponse.json(HttpCode.ACCEPTED, output)
