#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from blueprints.schemas.mon_infra import \
     MonitoringInfrastructure as MonInfraSchema
from common.config.modules.module_catalogue import ModuleCatalogue
from common.exception import exception
from common.server.endpoints import SOEndpoints
from common.server.http.http_code import HttpCode
from fastapi import APIRouter, Request
from typing import List, Optional, Union
import requests


router = APIRouter()
mod_c = ModuleCatalogue().modules()
ep_base = "http://so-{0}:{1}/{0}".format(
        "mon", mod_c.get("mon", {}).get("port", ""))


# When response_model is set, pydantic is enforced. However, enforcing
# one only would be problematic when a user selects a particular
# Accept-Type. Thus, "Union[x, y]" is used to allow both models x and y
@router.get(SOEndpoints.INFRA, response_model=Union[List[MonInfraSchema], str],
            status_code=HttpCode.OK)
@exception.handle_exc_resp
def infra_list(request: Request, id: Optional[str] = None):
    """
    Details on infrastructure nodes.
    """
    requests_ep = "{}/infra".format(ep_base)
    if id is not None:
        requests_ep = "{}?id={}".format(requests_ep, id)
    return requests.get(requests_ep)


@router.get(SOEndpoints.INFRA_SVC, status_code=HttpCode.OK)
@exception.handle_exc_resp
def infra_service_list(request: Request, infra_id: Optional[str] = None,
                       id: Optional[str] = None):
    """
    Details on services (NS) running in the infrastructure.
    """
    requests_ep = "{}/infra/service".format(ep_base)
    if infra_id is not None:
        requests_ep = "{}?infra-id={}".format(requests_ep, infra_id)
        if id is not None:
            requests_ep = "{}&id={}".format(requests_ep, id)
    else:
        if id is not None:
            requests_ep = "{}?id={}".format(requests_ep, id)
    return requests.get(requests_ep)


# TODO: call new MON methods from here

@router.get(SOEndpoints.TARGETS, status_code=HttpCode.OK)
@exception.handle_exc_resp
def prometheus_targets_list(request: Request):
    """
    List of Prometheus targets.
    """
    requests_ep = "{}/targets".format(ep_base)
    return requests.get(requests_ep)


@router.get(SOEndpoints.TARGETS_METRICS, status_code=HttpCode.OK)
@exception.handle_exc_resp
def prometheus_targets_metrics(request: Request):
    """
    Metrics for monitored targets, providing values for both
    generic (Prometheus) and custom (explicitly registered) metrics
    """
    requests_ep = "{}/targets/metrics".format(ep_base)
    return requests.get(requests_ep)
