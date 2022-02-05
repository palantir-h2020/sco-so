#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from blueprints.schemas.mon_infra import \
     MonitoringInfrastructure as MonInfraSchema
from common.config.api.api_categories import APICategories
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response_fastapi import HttpResponse
from fastapi import APIRouter, Request
from typing import List, Optional, Union
import requests


router = APIRouter()
api_c = APICategories().categories()
ep_base = "http://so-{0}:{1}/{0}".format(
        "mon", api_c.get("mon", {}).get("port", ""))


def get_response_out(result, content_type: str):
    try:
        result = result.json()
    except Exception:
        result = result.text
    return content.convert_to_ct(result, content_type)


# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Content-Type. Thus, "Union[x, y]" is used to allow both models x and y
@router.get("/infra", response_model=Union[List[MonInfraSchema], str],
            status_code=HttpCode.OK)
def infra_list(request: Request,
               id: Optional[str] = None, name: Optional[str] = None):
    """
    Details on infrastructure nodes.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")

    requests_ep = "{}/infra".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    elif name is not None:
        requests_ep = "{}?name={}".format(requests_ep, id)
    result = requests.get(requests_ep)
    try:
        result = get_response_out(result, content_type)
        return HttpResponse.infer(result)
    except Exception as e:
        return HttpResponse.infer({"output": str(e)},
                                  request.headers, HttpCode.INTERNAL_ERROR)
