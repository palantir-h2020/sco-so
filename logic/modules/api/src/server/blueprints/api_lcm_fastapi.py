#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from blueprints.schemas.lcm_ns import NSInstanceAction, \
        NSInstanceDeployment
from common.config.modules.module_catalogue import ModuleCatalogue
from common.exception import exception
from common.server.http.http_code import HttpCode
from common.server.endpoints import SOEndpoints
from fastapi import APIRouter, Request
from typing import Optional
import json
import requests


router = APIRouter()
mod_c = ModuleCatalogue().modules()
ep_base = "http://so-{0}:{1}/{0}".format(
        "lcm", mod_c.get("lcm", {}).get("port", ""))


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
    requests_ep = "{}/ns".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    return requests.get(requests_ep)


@router.post(SOEndpoints.NS, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_inst_deploy(request: Request, ns_pkg_id: str,
                   deploy_data: NSInstanceDeployment = None,
                   ):
    """
    Instantiate a new NS.
    """
    requests_ep = "{}/ns".format(ep_base)
    params_dict = {
        "ns-pkg-id": ns_pkg_id, "description": deploy_data.description,
        "vim-id": deploy_data.vim_id, "name": deploy_data.name,
        "ssh-keys": deploy_data.ssh_key,
        "ns-action-name": deploy_data.action_name,
        "ns-action-params": deploy_data.action_params
    }
    try:
        params_dict["ns-action-params"] = json.dumps(
            params_dict.get("ns-action-params"))
    except Exception:
        pass
    return requests.post(requests_ep, data=params_dict)


@router.delete(SOEndpoints.NS, status_code=HttpCode.ACCEPTED)
@exception.handle_exc_resp
def ns_inst_delete(request: Request, id: str,
                   force: Optional[str] = False):
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
def ns_inst_exec_action(request: Request, id: str,
                        action_data: NSInstanceAction = None,
                        ):
    """
    Execute action in specific NS.

    Bult-in actions: "terminate".
    """
    requests_ep = "{}/ns/action?id={}".format(ep_base, id)
    action_dict = {
        "ns-action-name": action_data.action_name,
        "ns-action-params": action_data.action_params
    }
    try:
        action_dict["ns-action-params"] = json.dumps(
            action_dict.get("ns-action-params"))
    except Exception:
        pass
    return requests.post(requests_ep, data=action_dict)


@router.get(SOEndpoints.XNF, status_code=HttpCode.OK)
@exception.handle_exc_resp
def xnf_inst_list(request: Request,
                  id: Optional[str] = None):
    """
    Details on xNF running instances.
    """
    requests_ep = "{}/xnf".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    return requests.get(requests_ep)
