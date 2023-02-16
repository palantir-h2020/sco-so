#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common.exception import exception
from common.infra.topology import NetworkLandscape
from common.server.endpoints import SOEndpoints
from common.server.http.content import AllowedContentTypes
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint, request


so_blueprints = Blueprint("so__cfg__infrastructure", __name__)


@so_blueprints.route(SOEndpoints.CFG_INFRASTRUCTURE, methods=["GET"])
@exception.handle_exc_resp
def list_infrastructure():
    _id = request.args.get("id")
    # TODO
    return {}


@so_blueprints.route(SOEndpoints.CFG_INFRASTRUCTURE, methods=["POST"])
@exception.handle_exc_resp
def create_infrastructure():
    request_params = request.form.to_dict()
    # TODO
    return {}


@so_blueprints.route(SOEndpoints.CFG_NFVO, methods=["GET"])
@exception.handle_exc_resp
def list_nfvo():
    _id = request.args.get("id")
    # TODO
    return {}


@so_blueprints.route(SOEndpoints.CFG_NFVO, methods=["POST"])
@exception.handle_exc_resp
def create_nfvo():
    request_params = request.form.to_dict()
    # TODO
    return {}


@so_blueprints.route(SOEndpoints.CFG_TOPOLOGY, methods=["GET"])
# @exception.handle_exc_resp
def list_network_topology():
    # FIXME handle in decorator
    accept_type = request.environ.get(
            "HTTP_ACCEPT_TYPE",
            request.environ.get("HTTP_ACCEPT"))
    # Provide JSON output by default (requirement)
    if accept_type is None:
        accept_type = AllowedContentTypes.CONTENT_TYPE_JSON.value
    _tenant_id = request.args.get("tenant-id")
    topology_stored = NetworkLandscape.topology_retrieval(_tenant_id)
    http_code = HttpCode.OK
    if topology_stored.get("topology") == {}:
        http_code = HttpCode.SERV_UNAV
    return HttpResponse.infer(topology_stored, http_code, accept_type)


@so_blueprints.route(SOEndpoints.CFG_TOPOLOGY, methods=["POST"])
# @exception.handle_exc_resp
def create_network_topology():
    # FIXME handle in decorator
    accept_type = request.environ.get(
            "HTTP_ACCEPT_TYPE",
            request.environ.get("HTTP_ACCEPT"))
    # Provide JSON output by default (requirement)
    if accept_type is None:
        accept_type = AllowedContentTypes.CONTENT_TYPE_JSON.value
    _tenant_id = request.args.get("tenant-id")
    # File is mandatory anyway, so it would never be None
    # TODO consider pushing a payload rather than a file itself
    # similar to LCM / instantiate or LCM / configure
    if request is not None and request.files is not None:
        _topo_data = request.files.get("file").read()
        _topo_data = _topo_data.decode("ascii")
    else:
        _topo_data = ""
    topology_stored = NetworkLandscape.topology_creation(
            _tenant_id, _topo_data)
    # topology_stored = json.dumps(topology_stored)
    return HttpResponse.infer(topology_stored, HttpCode.OK, accept_type)
