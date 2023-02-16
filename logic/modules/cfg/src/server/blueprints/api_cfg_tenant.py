#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common.exception import exception
from common.server.endpoints import SOEndpoints
from flask import Blueprint, request
# import json


so_blueprints = Blueprint("so__cfg__tenant", __name__)


@so_blueprints.route(SOEndpoints.CFG_TENANT, methods=["GET"])
@exception.handle_exc_resp
def list_tenants():
    _id = request.args.get("id")
    # TODO
    return {}


@so_blueprints.route(SOEndpoints.CFG_TENANT, methods=["POST"])
@exception.handle_exc_resp
def create_tenant():
    request_params = request.form.to_dict()
    # TODO
    return {}
