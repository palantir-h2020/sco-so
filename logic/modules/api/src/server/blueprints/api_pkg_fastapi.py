#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


# from blueprints.schemas.mon_infra import \
#      MonitoringInfrastructure as MonInfraSchema
from common.config.api.api_categories import APICategories
from common.exception import exception
from common.server.endpoints import SOEndpoints
from common.server.http.http_code import HttpCode
from common.server.http.http_response_fastapi import HttpResponse
from fastapi import APIRouter, File, Request, UploadFile
from typing import Optional
# from typing import List, Optional, Union
import requests


router = APIRouter()
api_c = APICategories().categories()
ep_base = "http://so-{0}:{1}/{0}".format(
        "pkg", api_c.get("pkg", {}).get("port", ""))


# TODO: enforce returned models
# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Accept-Type. Thus, "Union[x, y]" is used to allow both models x and y
# @router.get("/xnf", response_model=Union[List[MonInfraSchema], str],
#             status_code=HttpCode.OK)

# xNF

@router.get(SOEndpoints.XNF, status_code=HttpCode.OK)
@exception.handle_exc_resp
def xnf_pkg_list(request: Request, id: Optional[str] = None,
                 name: Optional[str] = None) -> HttpResponse:
    """
    Details on xNF packages.
    """
    requests_ep = "{}/xnf".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    elif name is not None:
        requests_ep = "{}?name={}".format(requests_ep, name)
    return requests.get(requests_ep)


@router.post(SOEndpoints.XNF, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def xnf_pkg_onboard(request: Request,
                    package: UploadFile = File(
                        ..., description="xNF in a .tar.gz")) -> HttpResponse:
    """
    Uploads an xNF package as a .tar.gz file.
    """
    requests_ep = "{}/xnf".format(ep_base)
    file_data = {"file": package.file.read()}
    return requests.post(requests_ep, files=file_data)


@router.delete(SOEndpoints.XNF, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def xnf_pkg_delete(request: Request, id: str) -> HttpResponse:
    """
    Delete specific xNF package.
    """
    requests_ep = "{}/xnf?id={}".format(ep_base, id)
    return requests.delete(requests_ep)


# NS

@router.get(SOEndpoints.NS, status_code=HttpCode.OK)
@exception.handle_exc_resp
def ns_pkg_list(request: Request, id: Optional[str] = None,
                name: Optional[str] = None) -> HttpResponse:
    """
    Details on NS packages.
    """
    requests_ep = "{}/ns".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    elif name is not None:
        requests_ep = "{}?name={}".format(requests_ep, name)
    return requests.get(requests_ep)


@router.post(SOEndpoints.NS, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_pkg_onboard(request: Request,
                   package: UploadFile = File(
                        ..., description="NS in a .tar.gz")) -> HttpResponse:
    """
    Uploads a NS package as a .tar.gz file.
    """
    requests_ep = "{}/ns".format(ep_base)
    file_data = {"file": package.file.read()}
    return requests.post(requests_ep, files=file_data)


@router.delete(SOEndpoints.NS, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_pkg_delete(request: Request, id: str) -> HttpResponse:
    """
    Delete specific NS package.
    """
    requests_ep = "{}/ns?id={}".format(ep_base, id)
    return requests.delete(requests_ep)
