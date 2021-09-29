#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from flask import Blueprint, request
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from server.logic.prometheus_targets import PrometheusTarget
from server.logic.vim import VIM
from server.logic.vnf import VNF


so_blueprints = Blueprint("so__mon__base", __name__)
prometheus_targets_handler = PrometheusTarget()


@so_blueprints.route("/mon", methods=["GET"])
def base() -> HttpResponse:
    data = {"name": "mon_api"}
    return HttpResponse.formatted(data, HttpCode.OK)


@so_blueprints.route("/mon/vim", methods=["GET"])
def vim_list() -> HttpResponse:
    data = VIM.vim_list()
    return HttpResponse.formatted(data, HttpCode.OK)


@so_blueprints.route("/mon/vnf", methods=["GET"])
def vnf_list() -> HttpResponse:
    data = VNF.vnf_list()
    return HttpResponse.formatted(data, HttpCode.OK)


@so_blueprints.route("/mon/targets", methods=["GET"])
def target_list() -> HttpResponse:
    data = {"targets": prometheus_targets_handler.targets_list()}
    return HttpResponse.formatted(data, HttpCode.OK)


@so_blueprints.route("/mon/targets", methods=["POST", "PUT", "DELETE"])
def handle_targets() -> HttpResponse:
    return_code = prometheus_targets_handler.update_target(request)
    return HttpResponse.formatted({}, return_code)
