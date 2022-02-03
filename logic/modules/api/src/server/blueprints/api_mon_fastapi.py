#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from blueprints.schemas.mon_infra import \
     MonitoringInfrastructure as MonInfraSchema
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response_fastapi import HttpResponse
from fastapi import APIRouter, Request
from typing import Union, List, Optional
import requests


router = APIRouter()
# FIXME: fetch MODL_NAME and MODL_API_PORT
# from configuration files
ep_base = "http://so-mon:50106/mon"


# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Content-Type. Thus, "Union[x, y]" is used to allow both models x and y
@router.get("/infra", response_model=Union[List[MonInfraSchema], str],
            status_code=HttpCode.OK)
def infra_list(request: Request,
               id: Optional[str] = "", name: Optional[str] = ""):
    """
    Details on infrastructure nodes.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    infra_list_output = requests.get("{}/infra".format(ep_base))
    try:
        result = infra_list_output.json()
        return content.convert_to_ct(result, content_type)
    except Exception as e:
        return HttpResponse.infer({"output": str(e)},
                                  request.headers, HttpCode.INTERNAL_ERROR)
