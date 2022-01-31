# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
#
# Licensed under ???


from flask import Blueprint
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse

import os


so_blueprints = Blueprint("server__base", __name__)


@so_blueprints.route("/", methods=["GET"])
def root():
    data = {"name": str(os.getenv("SO_MODL_NAME", "server_base"))}
    return HttpResponse.formatted(data, HttpCode.OK)


@so_blueprints.route("/status", methods=["GET"])
def status():
    data = {"status": "success"}
    return HttpResponse.formatted(data, HttpCode.OK)
