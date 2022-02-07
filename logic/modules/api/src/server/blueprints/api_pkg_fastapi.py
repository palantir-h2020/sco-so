#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


# from blueprints.schemas.mon_infra import \
#      MonitoringInfrastructure as MonInfraSchema
from common.config.api.api_categories import APICategories
from common.server.http.http_code import HttpCode
from common.server.http.http_response_fastapi import HttpResponse
from common.utils.osm_response_parsing import OSMResponseParsing
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
# Content-Type. Thus, "Union[x, y]" is used to allow both models x and y
# @router.get("/vnf", response_model=Union[List[MonInfraSchema], str],
#             status_code=HttpCode.OK)

# VNF

@router.get("/vnf", status_code=HttpCode.OK)
def vnf_pkg_list(request: Request, id: Optional[str] = None,
                 name: Optional[str] = None) -> HttpResponse:
    """
    Details on NF packages.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    requests_ep = "{}/vnf".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    elif name is not None:
        requests_ep = "{}?id={}".format(requests_ep, name)
    result = requests.get(requests_ep)
    return OSMResponseParsing.parse_normal(result, content_type)


@router.post("/vnf", status_code=HttpCode.ACCEPTED)
def vnf_pkg_onboard(request: Request,
                    package: UploadFile = File(
                        ..., description="VNF in a .tar.gz")) -> HttpResponse:
    """
    Onboard a VNF from a .tar.gz file.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    requests_ep = "{}/vnf".format(ep_base)
    file_data = {"file": package.file.read()}
    result = requests.post(requests_ep, files=file_data)
    return OSMResponseParsing.parse_normal(result, content_type)


@router.delete("/vnf", status_code=HttpCode.ACCEPTED)
def vnf_pkg_delete(request: Request, id: str) -> HttpResponse:
    """
    Delete specific NF package.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    # Note: in Flask this would be
    # content_type = request.environ.get("HTTP_ACCEPT")
    requests_ep = "{}/vnf?id={}".format(ep_base, id)
    result = requests.delete(requests_ep)
    parsed_result = OSMResponseParsing.parse_generic(result, content_type)
    if "internal-error" not in parsed_result.keys():
        return HttpResponse.infer({
            "output": parsed_result.get("response")},
            parsed_result.get("status-code"))
    else:
        return HttpResponse.infer({
            "output": parsed_result.get("response"),
            "internal-error": parsed_result.get("internal-error")},
            parsed_result.get("status-code"))


# NS

@router.get("/ns", status_code=HttpCode.OK)
def ns_pkg_list(request: Request, id: Optional[str] = None,
                name: Optional[str] = None) -> HttpResponse:
    """
    Details on NS packages.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    requests_ep = "{}/ns".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    elif name is not None:
        requests_ep = "{}?id={}".format(requests_ep, name)
    result = requests.get(requests_ep)
    return OSMResponseParsing.parse_normal(result, content_type)


@router.post("/ns", status_code=HttpCode.ACCEPTED)
def ns_pkg_onboard(request: Request,
                   package: UploadFile = File(
                        ..., description="NS in a .tar.gz")) -> HttpResponse:
    """
    Onboard a NS from a .tar.gz file.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    requests_ep = "{}/ns".format(ep_base)
    file_data = {"file": package.file.read()}
    result = requests.post(requests_ep, files=file_data)
    return OSMResponseParsing.parse_normal(result, content_type)


# FIXME: not submitting request
@router.delete("/ns", status_code=HttpCode.ACCEPTED)
def ns_pkg_delete(request: Request, id: str) -> HttpResponse:
    """
    Delete specific NS package.
    """
    content_type = "application/json"
    if "content-type" in request.headers:
        content_type = request.headers.get("content-type")
    requests_ep = "{}/ns?id={}".format(ep_base, id)
    result = requests.delete(requests_ep)
    parsed_result = OSMResponseParsing.parse_generic(result, content_type)
    if "internal-error" not in parsed_result.keys():
        return HttpResponse.infer(
            parsed_result.get("response"),
            parsed_result.get("status-code"))
        return parsed_result
#        return parsed_result.get("response")
#        return HttpResponse.infer({
#            "output": parsed_result.get("response")},
#            parsed_result.get("status-code"))
    else:
        return HttpResponse.infer({
            "output": parsed_result.get("response"),
            "internal-error": parsed_result.get("internal-error")},
            parsed_result.get("status-code"))
