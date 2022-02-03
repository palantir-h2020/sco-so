#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.exception.exception import SOException
from common.log.log import setup_custom_logger
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from common.server.views.infra import check_auth_params
from common.server.views.infra import check_isolation_params
from flask import Blueprint
from flask import request
from nfv.ns import VnsfoNs
from server.endpoints import VnsfoEndpoints as endpoints

import configparser


CONFIG_PATH = "./"
LOGGER = setup_custom_logger(__name__)


so_views = Blueprint("so_ns_views", __name__)


@so_views.route(endpoints.NS_C_NSS, methods=["GET"])
@so_views.route(endpoints.NS_C_NSS_R2, methods=["GET"])
def fetch_config_nss():
    ns_object = VnsfoNs()
    return HttpResponse.json(HttpCode.OK, ns_object.fetch_config_nss())


@so_views.route(endpoints.NS_C_NSS_R4, methods=["GET"])
def fetch_config_nss_r4():
    ns_object = VnsfoNs(4)
    return HttpResponse.json(HttpCode.OK,
                             ns_object.fetch_config_nss())


def get_attack_ns_mapping(attack_type):
    config = configparser.ConfigParser()
    config.read("{0}conf/attacks.conf".format(CONFIG_PATH))
    ns_mapped = config["general"].get(attack_type, "default").lower()
    return ns_mapped


def instantiate_ns_request_check():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    exp_params_implicit = ["attack_type"]
    exp_params_explicit = ["ns_name", "instance_name"]
    if not content.data_in_request(request, exp_params_implicit) and \
            not content.data_in_request(request, exp_params_explicit):
        SOException.improper_usage(
                "Missing parameters: any of {} or {}"
                .format(exp_params_implicit, exp_params_explicit))
    if (content.data_in_request(request, exp_params_implicit) and
            content.data_in_request(request, exp_params_explicit)):
        SOException.improper_usage(
                "Conflicting parameters: {} and {} cannot coexist"
                .format(exp_params_implicit, exp_params_explicit))
    instantiation_data = request.get_json()
    # When an attack type is provided, the SO consults the internal
    # mapping between Network Services and attacks and picks the NS
    # that is pointed by the given attack
    if content.data_in_request(request, exp_params_implicit):
        instantiation_data["ns_name"] = get_attack_ns_mapping(
                instantiation_data["attack_type"])
        instantiation_data["instance_name"] = "%s_%s" % (
                instantiation_data["ns_name"],
                instantiation_data["attack_type"])
    return instantiation_data


@so_views.route(endpoints.NS_INSTANTIATE, methods=["POST"])
@so_views.route(endpoints.NS_INSTANTIATE_R2, methods=["POST"])
@content.expect_json_content
def instantiate_ns():
    instantiation_data = instantiate_ns_request_check()
    if "authentication" in instantiation_data:
        missing_params = check_auth_params(
            instantiation_data["authentication"])
        if len(missing_params) > 0:
            msg = "Missing authentication parameters {0}".format(
                ", ".join(missing_params))
            LOGGER.info(msg)
            SOException.improper_usage(msg)
    if "isolation_policy" in instantiation_data:
        missing_params = check_isolation_params(
            instantiation_data["isolation_policy"])
        if len(missing_params) > 0:
            msg = "Missing isolation policy parameters {0}".format(
                    ", ".join(missing_params))
            LOGGER.info(msg)
            SOException.improper_usage(msg)
    if "termination_policy" in instantiation_data:
        missing_params = check_isolation_params(
            instantiation_data["termination_policy"])
        if len(missing_params) > 0:
            msg = "Missing termination policy parameters {0}".format(
                    ", ".join(missing_params))
            LOGGER.info(msg)
            SOException.improper_usage(msg)
    ns_object = VnsfoNs()
    result = ns_object.instantiate_ns(instantiation_data)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)


@so_views.route(endpoints.NS_INSTANTIATE_R4, methods=["POST"])
@content.expect_json_content
def instantiate_ns_r4():
    instantiation_data = instantiate_ns_request_check()
    ns_object = VnsfoNs(4)
    result = ns_object.instantiate_ns(instantiation_data)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["status_code"],
                                 result["error_response"])


@so_views.route(endpoints.NS_R_NSS, methods=["GET"])
@so_views.route(endpoints.NS_R_NSS_ID, methods=["GET"])
@so_views.route(endpoints.NS_R_NSS_R2, methods=["GET"])
@so_views.route(endpoints.NS_R_NSS_ID_R2, methods=["GET"])
def fetch_running_nss(instance_id=None):
    ns_object = VnsfoNs()
    nss = ns_object.get_nsr_running(instance_id)
    return HttpResponse.json(HttpCode.OK, nss)


@so_views.route(endpoints.NS_R_NSS_R4, methods=["GET"])
@so_views.route(endpoints.NS_R_NSS_ID_R4, methods=["GET"])
def fetch_running_nss_r4(instance_id=None):
    ns_object = VnsfoNs(4)
    nss = ns_object.get_nsr_running(instance_id)
    return HttpResponse.json(HttpCode.OK, nss)


@so_views.route(endpoints.NS_R_NSS)
@so_views.route(endpoints.NS_R_NSS_ID, methods=["DELETE"])
@so_views.route(endpoints.NS_R_NSS_R2)
@so_views.route(endpoints.NS_R_NSS_ID_R2, methods=["DELETE"])
def delete_ns(instance_id=None):
    ns_object = VnsfoNs()
    result = ns_object.delete_ns(instance_id)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)


@so_views.route(endpoints.NS_R_NSS_R4)
@so_views.route(endpoints.NS_R_NSS_ID_R4, methods=["DELETE"])
def delete_ns_r4(instance_id=None):
    ns_object = VnsfoNs(4)
    result = ns_object.delete_ns(instance_id)
    if result.get("result", "") == "success":
        return HttpResponse.json(HttpCode.OK, result)
    else:
        return HttpResponse.json(result["error_response"].status_code,
                                 result["error_response"].text)
