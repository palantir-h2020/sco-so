#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint


so_blueprints = Blueprint("so__api__base", __name__)


@so_blueprints.route("/api", methods=["GET"])
def base():
    data = {"name": "api_api"}
    return HttpResponse.infer(data, HttpCode.OK)
