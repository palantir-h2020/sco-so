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
ep_base = "http://so-lcm:50105/lcm"


# TODO: enforce returned models
# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Content-Type. Thus, "Union[x, y]" is used to allow both models x and y
# @router.get("/infra", response_model=Union[List[MonInfraSchema], str],
#             status_code=HttpCode.OK)
@router.get("/ns", status_code=HttpCode.OK)
def ns_inst_list(request: Request,
                 id: Optional[str] = None):
    """
    Details on NS running instances.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    requests_ep = "{}/ns".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    ns_inst_output = requests.get(requests_ep)
    try:
        result = ns_inst_output.json()
        return content.convert_to_ct(result, content_type)
    except Exception as e:
        return HttpResponse.infer({"output": str(e)},
                                  request.headers, HttpCode.INTERNAL_ERROR)


# FIXME: check output returned from LCM
# ValueError: [TypeError("'property' object is not iterable"),
# TypeError('vars() argument must have __dict__ attribute')]
# {"action":"delete","instance-id":"ea9df2f9-edca-4f38-9c1b-8038451244d3","result":"success"}
@router.delete("/ns", status_code=HttpCode.ACCEPTED)
def ns_inst_delete(request: Request, id: str):
    """
    Delete running NS instance.
    """
    try:
        requests_ep = "{}/ns/{}".format(ep_base, id)
        return requests.delete(requests_ep)
    except Exception as e:
        return HttpResponse.infer({"output": str(e)},
                                  request.headers, HttpCode.INTERNAL_ERROR)


@router.get("/vnf", status_code=HttpCode.OK)
def vnf_inst_list(request: Request,
                  id: Optional[str] = None):
    """
    Details on VNF running instances.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    requests_ep = "{}/vnf".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    vnf_inst_output = requests.get(requests_ep)
    try:
        result = vnf_inst_output.json()
        return content.convert_to_ct(result, content_type)
    except Exception as e:
        return HttpResponse.infer({"output": str(e)},
                                  request.headers, HttpCode.INTERNAL_ERROR)
