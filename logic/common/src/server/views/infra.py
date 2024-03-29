#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.exception.exception import SOException
from common.log.log import setup_custom_logger
from flask import abort
from flask import Blueprint
from flask import current_app
from flask import request
from infra.network import Network
from infra.network import NetworkConnectException
from infra.node import Node
from infra.node import NodeSSHException
from common.server.endpoints import VnsfoEndpoints as endpoints
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse

import bson


LOGGER = setup_custom_logger(__name__)


so_views = Blueprint("so_infra_views", __name__)


@so_views.route(endpoints.NFVI_NETWORK_REF_FLOWS, methods=["GET"])
def get_network_reference_flows():
    """
    Fetch reference flows to be compared against those in the switch (by TM).
    """
    flows_data = Network().get_network_reference_flows()
    return HttpResponse.json(HttpCode.OK, flows_data)


@so_views.route(endpoints.NFVI_NETWORK_C_FLOW, methods=["GET"])
@so_views.route(endpoints.NFVI_NETWORK_C_FLOW_ID, methods=["GET"])
def get_network_device_config_flows(flow_id=None):
    """
    Config in the SO: DB
    """
    flows_data = Network().get_last_network_device_config_flow(flow_id)
    return HttpResponse.json(HttpCode.OK, flows_data)


@so_views.route(endpoints.NFVI_NETWORK_R_FLOW, methods=["GET"])
@so_views.route(endpoints.NFVI_NETWORK_R_FLOW_ID, methods=["GET"])
def get_network_device_running_flows(flow_id=None):
    """
    Config in the SO: ODL
    """
    flows_data = Network().get_network_device_running_flows(flow_id)
    return HttpResponse.json(HttpCode.OK, flows_data)


@so_views.route(endpoints.NFVI_NETWORK_C_FLOW, methods=["POST"])
@so_views.route(endpoints.NFVI_NETWORK_C_FLOW_ID, methods=["POST"])
def store_network_device_config_flow(flow_id=None, flow=None):
    """
    Config in the SO: DB
    """
    exp_ct = "application/xml"
    header_ct = request.headers.get("Content-Type", "")
    if header_ct is not None and exp_ct not in header_ct:
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    flow = request.data
    flow_data = Network().store_network_device_config_flow(flow_id, flow, True)
    return HttpResponse.json(HttpCode.OK, flow_data)


@so_views.route(endpoints.NFVI_NETWORK_R_FLOW, methods=["POST"])
@so_views.route(endpoints.NFVI_NETWORK_R_FLOW_ID, methods=["POST"])
def store_network_device_running_flow(flow_id=None, flow=None):
    """
    Running in the SO: ODL
    Stores data in running (and config)
    """
    exp_ct = ["application/xml", "application/json"]
    header_ct = request.headers.get("Content-Type", "")
    # Internal calls will come from other methods and provide a specific flag
    # In such situations, the Content-Type will be defined internally
    if header_ct is not None and not \
            any(map(lambda ct: ct in header_ct, exp_ct)):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    flow = request.data
    Network().store_network_device_running_flow(flow_id, flow)
    # Trigger attestation right after SDN rules are inserted
    last_trusted_flow = Network()\
        .get_last_network_device_config_flow().get("flow")
    attest_data = None
    try:
        attest_data = Network().attest_and_revert_switch()
    except NetworkConnectException as e:
        SOException.internal_error(str(e))
    if not attest_data or attest_data is None:
        SOException.internal_error("Cannot attest status of the device(s)")
    # Indicate whether the flows should keep the trusted state or not
    # For externally (manually pushed) rules, mark these as trusted
    is_device_trusted = True if attest_data.get("result", "") == \
        "flow_trusted" else False
    flow_data = None
    # Save flow in "reference" DB (as untrusted) in case the state is trusted
    flow_data = Network().store_network_device_config_flow(
                flow_id, last_trusted_flow, False, is_device_trusted)
    return HttpResponse.json(HttpCode.OK, flow_data)


@so_views.route(endpoints.NFVI_NETWORK_C_FLOW, methods=["DELETE"])
@so_views.route(endpoints.NFVI_NETWORK_C_FLOW_ID, methods=["DELETE"])
def delete_network_device_config_flow(flow_id=None):
    flow_data = Network().delete_network_device_config_flow()
    return HttpResponse.json(HttpCode.OK, flow_data)


@so_views.route(endpoints.NFVI_NETWORK_R_FLOW, methods=["DELETE"])
@so_views.route(endpoints.NFVI_NETWORK_R_FLOW_ID, methods=["DELETE"])
def delete_network_device_running_flow(flow_id=None):
    """
    Running in the SO: ODL
    Deletes data from running only
    """
    flow_data = Network().delete_network_device_running_flow(flow_id)
    return HttpResponse.json(HttpCode.OK, flow_data)


@so_views.route(endpoints.NFVI_NODE_ID, methods=["DELETE"])
def delete_node(node_id):
    Node(node_id).delete()
    return ("", HttpCode.NO_CONTENT)


@so_views.route(endpoints.NFVI_NODE, methods=["GET"])
@so_views.route(endpoints.NFVI_NODE_ID, methods=["GET"])
def get_nodes(node_id=None):
    if node_id is not None:
        if bson.objectid.ObjectId.is_valid(node_id) is False:
            SOException.improper_usage("Bad node_id: {0}".format(node_id))
    nodes = current_app.mongo.get_nodes(node_id)
    return HttpResponse.json(HttpCode.OK, nodes)


@so_views.route(endpoints.NFVI_NODE_PHYSICAL, methods=["GET"])
def get_nodes_physical():
    nodes = current_app.mongo.get_phys_virt_nodes(physical=True)
    return HttpResponse.json(HttpCode.OK, nodes)


@so_views.route(endpoints.NFVI_NODE_PHYSICAL_ISOLATED, methods=["GET"])
def get_nodes_physical_isolated(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=True,
                                                  isolated=True)
    return HttpResponse.json(HttpCode.OK, nodes)


@so_views.route(endpoints.NFVI_NODE_PHYSICAL_TRUSTED, methods=["GET"])
def get_nodes_physical_trusted(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=True,
                                                  isolated=False)
    return HttpResponse.json(HttpCode.OK, nodes)


@so_views.route(endpoints.NFVI_NODE_VIRTUAL, methods=["GET"])
def get_nodes_virtual():
    nodes = current_app.mongo.get_phys_virt_nodes(physical=False)
    return HttpResponse.json(HttpCode.OK, nodes)


@so_views.route(endpoints.NFVI_NODE_VIRTUAL_ISOLATED, methods=["GET"])
def get_nodes_virtual_isolated(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=False,
                                                  isolated=True)
    return HttpResponse.json(HttpCode.OK, nodes)


@so_views.route(endpoints.NFVI_NODE_VIRTUAL_TRUSTED, methods=["GET"])
def get_nodes_virtual_trusted(node_id=None):
    nodes = current_app.mongo.get_phys_virt_nodes(physical=False,
                                                  isolated=False)
    return HttpResponse.json(HttpCode.OK, nodes)


@so_views.route(endpoints.NFVI_NODE_ISOLATE, methods=["POST"])
def isolate(node_id):
    try:
        Node(node_id).isolate()
    except NodeSSHException:
        abort(500)
    return ('', HttpCode.NO_CONTENT)


@so_views.route(endpoints.NFVI_NODE_TERMINATE, methods=["POST"])
def terminate(node_id):
    try:
        Node(node_id).terminate()
    except NodeSSHException:
        abort(500)
    return ('', HttpCode.NO_CONTENT)


@so_views.route(endpoints.NFVI_NODE_ID, methods=["PUT"])
def config_node(node_id):
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    config_data = request.get_json()
    fields = ["isolated", "disabled", "terminated"]
    action = None
    for field in fields:
        if field in config_data:
            action = field
    if action is None:
        SOException.improper_usage("Config should be isolated or disabled")
    if type(config_data[action]) is not bool:
        SOException.improper_usage("{0} should be bool".format(action))
    if action == "isolated" and config_data[action] is True:
        try:
            Node(node_id).isolate()
        except NodeSSHException:
            abort(500)
    elif config_data[action] is False:
        SOException.improper_usage(
                "Automated isolation revert not supported")
    if action == "terminated" and config_data[action] is True:
        try:
            Node(node_id).terminate()
        except NodeSSHException:
            abort(500)
    elif config_data[action] is False:
        SOException.improper_usage(
                "Automated termination revert not supported")
    if action == "disabled" and config_data[action] is True:
        Node(node_id).disable()
    return ('', HttpCode.NO_CONTENT)


@so_views.route(endpoints.NFVI_NODE, methods=["POST"])
def register_node():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    node_data = request.get_json(silent=True)
    if node_data is None:
        SOException.improper_usage(
                "Body content does not follow type: {0}"
                .format(exp_ct))
    missing_params = check_node_params(node_data)
    if len(missing_params) > 0:
        SOException.improper_usage("Missing node parameters: {0}".format(
            ", ".join(missing_params)))
    missing_auth_params = check_auth_params(node_data["authentication"])
    if len(missing_auth_params) > 0:
        SOException.improper_usage(
            "Missing authentication parameters: {0}".format(
                ", ".join(missing_auth_params)))
    missing_isolation_params = check_isolation_params(
        node_data["isolation_policy"])
    if len(missing_isolation_params) > 0:
        SOException.improper_usage("Missing isolation parameters: {0}".format(
            ", ".join(missing_isolation_params)))
    missing_termination_params = check_isolation_params(
        node_data["termination_policy"])
    if len(missing_termination_params) > 0:
        SOException.improper_usage(
                "Missing termination parameters: {0}".format(
                    ", ".join(missing_termination_params)))
    node_id = current_app.mongo.store_node_information(node_data)
    if "switch" in node_data.get("driver", "").lower():
        Network().attest_and_revert_switch()
    return HttpResponse.json(HttpCode.OK, {"node_id": node_id})


def check_isolation_params(isolation_policy):
    params = ["name", "type"]
    missing_params = []
    for param in params:
        if param not in isolation_policy:
            missing_params.append(param)
            return missing_params
    if isolation_policy["type"] not in ("ifdown", "delflow", "shutdown"):
        msg = "Isolation type should be ifdown, delflow or shutdown"
        LOGGER.info(msg)
        SOException.\
            improper_usage(msg)
    if isolation_policy["type"] == "ifdown":
        if "interface_name" not in isolation_policy:
            missing_params.append("interface_name")
    if isolation_policy["type"] == "delflow":
        df_params = ["switch", "target_filter"]
        for param in df_params:
            if param not in isolation_policy:
                missing_params.append(param)
    if isolation_policy["type"] == "shutdown":
        if "command" not in isolation_policy:
            missing_params.append("command")
    return missing_params


def check_auth_params(auth_data):
    params = ["username", "type"]
    missing_params = []
    for param in params:
        if param not in auth_data:
            missing_params.append(param)
            return missing_params
    if auth_data.get("type", "") not in ("password", "private_key"):
        msg = "Authentication type should be password or private_key"
        LOGGER.info(msg)
        SOException.\
            improper_usage(msg)
    if auth_data["type"] == "password":
        if "password" not in auth_data:
            missing_params.append("password")
    if auth_data["type"] == "private_key":
        if "private_key" not in auth_data:
            missing_params.append("private_key")
    return missing_params


def check_node_params(node_data):
    params = ["host_name", "ip_address", "pcr0", "driver",
              "analysis_type", "authentication",
              "isolation_policy", "termination_policy", "distribution"]
    missing_params = []
    for param in params:
        if param not in node_data:
            missing_params.append(param)
    return missing_params
