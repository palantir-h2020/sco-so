#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


# from blueprints.schemas.mon_infra import \
#      MonitoringInfrastructure as MonInfraSchema
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response_fastapi import HttpResponse
from fastapi import APIRouter, Request
from typing import Optional
# from typing import List, Optional, Union
import requests


router = APIRouter()
# FIXME: fetch MODL_NAME and MODL_API_PORT
# from configuration files
ep_base = "http://so-pkg:50107/pkg"


# TODO: enforce returned models
# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Content-Type. Thus, "Union[x, y]" is used to allow both models x and y
# @router.get("/infra", response_model=Union[List[MonInfraSchema], str],
#             status_code=HttpCode.OK)
@router.get("/ns", status_code=HttpCode.OK)
def ns_pkg_list(request: Request,
                id: Optional[str] = "", name: Optional[str] = ""):
    """
    Details on NS packages.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    ns_pkg_output = requests.get("{}/ns".format(ep_base))
    try:
        result = ns_pkg_output.json()
        return content.convert_to_ct(result, content_type)
    except Exception as e:
        return HttpResponse.infer({"output": str(e)},
                                  request.headers, HttpCode.INTERNAL_ERROR)


@router.get("/vnf", status_code=HttpCode.OK)
def vnf_pkg_list(request: Request,
                 id: Optional[str] = "", name: Optional[str] = ""):
    """
    Details on NF packages.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    vnf_pkg_output = requests.get("{}/vnf".format(ep_base))
    try:
        result = vnf_pkg_output.json()
        return content.convert_to_ct(result, content_type)
    except Exception as e:
        return HttpResponse.infer({"output": str(e)},
                                  request.headers, HttpCode.INTERNAL_ERROR)
