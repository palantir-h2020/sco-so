#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.server.http.http_code import HttpCode
from handlers.prometheus_targets_handler import PrometheusTargetsHandler
from common.db.mongo_connector import MongoConnector
#from common.db.models.prometheus_targets_model import PrometheusTargets
#from common.db.models.prometheus_targets_operation import PrometheusTargetsOperation
from flask import make_response


class PrometheusTarget(object):

    def __init__(self):
        # TODO: move file_name as var to the cfg/mon.api configuration
        targets_file_name = "/opt/prometheus-targets.json"
        self.target_handler = PrometheusTargetsHandler(targets_file_name)

    def target_list(self):
        # TODO: retrieve targets from the MongoDB
        return []

    def update_target(self, request) -> HttpCode:
        # TODO: persist all targets (added, edited, delete) in the common
        # DB (MongoDB)
        request_body = request.json
        target_url = ""
        new_url = ""
        return_code = HttpCode.OK
        if request_body is None:
            return make_response("Content-Type must be set to \
                    \"application/json\"", 400)
        # Get the "url" parameter from the JSON body
        if request.method in ["POST", "DELETE"]:
            target_url = request_body.get("url", None)
        elif request.method == "PUT":
            target_url = request_body.get("current-url", None)
            new_url = request_body.get("new-url", None)
        # Call each specific function
        # TODO: inside the PrometheusTargetsHandler there should be
        # introduced means to verify the content is properly
        # updated w.r.t. to the request, so this returns a boolean
        # flag indicating it suceeded or failed
        # and thus this change would be reflected in return_code
        if request.method == "POST":
            self.target_handler.add_target(target_url)
        elif request.method == "PUT":
            self.target_handler.replace_target(target_url, new_url)
        elif request.method == "DELETE":
            self.target_handler.delete_target(target_url)
        else:
            return_code = HttpCode.METH_NOT_ALLOW
        return return_code
