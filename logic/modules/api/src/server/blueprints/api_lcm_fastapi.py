#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


# from blueprints.schemas.mon_infra import \
#      MonitoringInfrastructure as MonInfraSchema
from common.config.api.api_categories import APICategories
from common.exception import exception
# from common.server.http import content
from common.server.http.http_code import HttpCode
# from common.server.http.http_response_fastapi import HttpResponse
from common.server.endpoints import SOEndpoints
from fastapi import APIRouter, Query, Request
from typing import List, Optional
import requests


router = APIRouter()
api_c = APICategories().categories()
ep_base = "http://so-{0}:{1}/{0}".format(
        "lcm", api_c.get("lcm", {}).get("port", ""))


# TODO: enforce returned models
# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Content-Type. Thus, "Union[x, y]" is used to allow both models x and y
# @router.get("/infra", response_model=Union[List[MonInfraSchema], str],
#             status_code=HttpCode.OK)
@router.get(SOEndpoints.NS, status_code=HttpCode.OK)
@exception.handle_exc_resp
def ns_inst_list(request: Request,
                 id: Optional[str] = None):
    """
    Details on NS running instances.
    """
    # content_type = "application/json"
    # if "content-type" in request.headers:
    #     content_type = request.headers.get("content-type")
    requests_ep = "{}/ns".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    return requests.get(requests_ep)


@router.post(SOEndpoints.NS, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_inst_deploy(request: Request, ns_pkg_id: str,
                   vim_id: Optional[str] = None,
                   name: Optional[str] = None,
                   description: Optional[str] = None,
                   ssh_key: Optional[List[str]] = Query(None),
                   action_name: Optional[str] = None,
                   action_params: Optional[str] = None,
                   ):
    """
    Instantiate a new NS.
    """
    requests_ep = "{}/ns".format(ep_base)
    params_dict = {
        "ns-pkg-id": ns_pkg_id, "vim-id": vim_id, "name": name,
        "description": description, "ssh-keys": ssh_key,
        "ns-action-name": action_name, "ns-action-params": action_params
    }
    return requests.post(requests_ep, data=params_dict)


@router.delete(SOEndpoints.NS, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_inst_delete(request: Request, id: str, force: Optional[bool]):
    """
    Delete running NS instance.
    """
    requests_ep = "{}/ns?id={}".format(ep_base, id)
    if force:
        requests_ep = "{}&force={}".format(requests_ep, force)
    return requests.delete(requests_ep)


@router.get(SOEndpoints.LCM_ACT, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_inst_get_actions(request: Request, id: str):
    """
    Details on executed actions for a given NS.
    """
    requests_ep = "{}/ns/action?id={}".format(ep_base, id)
    return requests.get(requests_ep)


@router.post(SOEndpoints.LCM_ACT, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_inst_exec_action(request: Request, id: str, action_name: str,
                        action_params: Optional[str] = None,
                        ):
    """
    Execute action in specific NS.

    Bult-in actions: "terminate".
    """
    requests_ep = "{}/ns/action?id={}".format(ep_base, id)
    action_dict = {
        "ns-action-name": action_name, "ns-action-params": action_params
    }
    return requests.post(requests_ep, data=action_dict)


@router.get(SOEndpoints.VNF, status_code=HttpCode.OK)
@exception.handle_exc_resp
def vnf_inst_list(request: Request,
                  id: Optional[str] = None):
    """
    Details on VNF running instances.
    """
    requests_ep = "{}/vnf".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    return requests.get(requests_ep)
