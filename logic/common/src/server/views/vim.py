#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.exception.exception import SOException
from common.server.endpoints import VnsfoEndpoints as endpoints
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint
from flask import request
from nfvi.vim import VnsfoVim as vim_s

so_views = Blueprint("so_vim_views", __name__)
so_xnf = vim_s()


@so_views.route(endpoints.VIM_LIST, methods=["GET"])
@content.expect_json_content
def get_vim_list():
    return HttpResponse.json(HttpCode.OK, so_xnf.get_vim_list())


@so_views.route(endpoints.VIM_IMAGE, methods=["GET"])
@content.expect_json_content
def get_vim_images():
    return HttpResponse.json(HttpCode.OK, so_xnf.get_vim_img_list())


@so_views.route(endpoints.VIM_IMAGE_UPLOAD, methods=["POST"])
@content.expect_json_content
def register_xnf_image(vim_id):
    exp_ct = "multipart/form-data"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    if not(len(request.files) > 0 and "image" in request.files.keys()):
        SOException.improper_usage("Missing file")
    img_bin = request.files.get("image")
    img_name = img_bin.filename
    # img_name = img_name[0:img_name.index(".")-1]
    output = so_xnf.register_vdu(vim_id, img_name, img_bin.stream)
    return HttpResponse.json(HttpCode.ACCEPTED, output)
