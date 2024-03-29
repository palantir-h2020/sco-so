#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from common.exception import exception
from common.server.endpoints import SOEndpoints
from common.server.http.http_response import HttpResponse
from flask import Blueprint, request
from server.logic.infra import Infra

so_blueprints = Blueprint("so__mon__infra", __name__)
infra_handler = Infra()


@so_blueprints.route(SOEndpoints.MON_INFRA, methods=["GET"])
@exception.handle_exc_resp
def infra_list() -> HttpResponse:
    _infra_id = request.args.get("id")
    return infra_handler.infra_list(_infra_id)


@so_blueprints.route(SOEndpoints.MON_INFRA_SVC, methods=["GET"])
@exception.handle_exc_resp
def infra_service_list() -> HttpResponse:
    _id = request.args.get("id")
    _infra_id = request.args.get("infra-id")
    return infra_handler.service_list(_infra_id, _id)
