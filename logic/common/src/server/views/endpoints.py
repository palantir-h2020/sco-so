#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from flask import Blueprint
from server.http.http_code import HttpCode
from server.http.http_response import HttpResponse
from server.endpoints import VnsfoEndpoints as endpoints_s

so_views = Blueprint("so_endpoint_views", __name__)
so_endpoints = endpoints_s()


@so_views.route(endpoints_s.ROOT, methods=["GET"])
def endpoints():
    ep_content = so_endpoints.api_endpoints()
    if "<html" in ep_content:
        return ep_content
    return HttpResponse.json(HttpCode.OK, ep_content)
