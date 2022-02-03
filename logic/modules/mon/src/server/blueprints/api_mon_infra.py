#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint, request
from server.logic.infra import Infra

so_blueprints = Blueprint("so__mon__infra", __name__)
infra_handler = Infra()


@so_blueprints.route("/mon/infra", methods=["GET"])
def infra_list() -> HttpResponse:
    infra_id = request.args.get("id")
    infra_name = request.args.get("name")
    filter_infra = infra_id
    if infra_id is None:
        filter_infra = infra_name
    data = infra_handler.infra_list(filter_infra)
    return HttpResponse.formatted(data, HttpCode.OK)
