#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from common.config.modules.module_catalogue import ModuleCatalogue
from common.exception import exception
from common.server.endpoints import SOEndpoints
from common.server.http.http_code import HttpCode
from common.server.http.http_response_fastapi import HttpResponse
from fastapi import APIRouter, File, Request, UploadFile
from typing import Optional
# from typing import List, Optional, Union
import requests


router = APIRouter()
mod_c = ModuleCatalogue().modules()
ep_base = "http://so-{0}:{1}/{0}".format(
        "cfg", mod_c.get("cfg", {}).get("port", ""))


# TODO: enforce returned models
# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Accept-Type. Thus, "Union[x, y]" is used to allow both models x and y
# @router.get("/xnf", response_model=Union[List[MonInfraSchema], str],
#             status_code=HttpCode.OK)

# Network topology

@router.get(SOEndpoints.TOPOLOGY, status_code=HttpCode.OK)
@exception.handle_exc_resp
def topology_list(request: Request, tenant_id: Optional[str] = None,
                  ) -> HttpResponse:
    """
    Details on the topology of all or one tenant.
    """
    accept_type = request.headers.get("accept-type")
    headers = {"Accept": accept_type}
    requests_ep = "{}/{}".format(ep_base, SOEndpoints.TOPOLOGY)
    if tenant_id is not None:
        requests_ep = "{}?tenant-id={}".format(requests_ep, tenant_id)
    return requests.get(requests_ep, headers=headers)


@router.post(SOEndpoints.TOPOLOGY, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def topology_create(request: Request,
                    tenant_id: str,
                    topology: UploadFile = File(
                     ..., description="Topology YAML file")) -> HttpResponse:
    """
    Uploads a topology file with low-level details on connectivity.
    """
    accept_type = request.headers.get("accept-type")
    headers = {"Accept": accept_type}
    requests_ep = "{}/{}?tenant-id={}".format(
        ep_base, SOEndpoints.TOPOLOGY, tenant_id)
    # File is mandatory anyway, so it would never be None
    if topology is not None and topology.file is not None:
        file_content = topology.file
        file_data = {"file": file_content}
    else:
        file_data = None
    # FIXME do not force - change file to textarea, pass Accept header somehow
    return requests.post(requests_ep, headers=headers, files=file_data)
