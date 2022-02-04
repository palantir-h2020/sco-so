#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from flask import Blueprint
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse


so_blueprints = Blueprint("so__pkg__base", __name__)


@so_blueprints.route("/pkg", methods=["GET"])
def base():
    data = {"name": "pkg_api"}
    return HttpResponse.formatted(data, HttpCode.OK)
