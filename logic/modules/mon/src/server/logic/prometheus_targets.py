#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.server.http.http_code import HttpCode
from common.utils.file_handling import FileHandling
from handlers.prometheus_targets_handler import PrometheusTargetsHandler
from flask import make_response
import os


class PrometheusTarget(object):

    def __init__(self):
        self.config = FullConfParser()
        self.mon_category = self.config.get("mon.yaml")
        self.prometheus_category = self.mon_category.get("prometheus")
        self.prom_targets_category = self.prometheus_category.get("targets")
        targets_file_name = self.prom_targets_category.get("file")
        common_path = FileHandling.extract_common_path(
            os.path.abspath(__file__),
            targets_file_name,
            "server")
        targets_file_name = os.path.normpath(
                        os.path.join(common_path, targets_file_name))
        if not os.path.isfile(targets_file_name):
            raise Exception(
                    "Configuration file {0} does not exist. ".format(
                        targets_file_name) +
                    "Check path in local mon.yaml file")
        self.target_handler = PrometheusTargetsHandler(targets_file_name)

    def targets_list(self):
        return self.target_handler.list_targets()

    def update_target(self, request) -> HttpCode:
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
        # FIXME: the comment below is not yet implemented
        # TODO: inside the PrometheusTargetsHandler there should be
        # introduced means to verify the content is properly
        # updated w.r.t. to the request, so this returns a boolean
        # flag indicating it suceeded or failed
        # and thus this change would be reflected in return_code
        if request.method == "POST":
            return_code = self.target_handler.add_target(target_url)
        elif request.method == "PUT":
            return_code = self.target_handler.replace_target(
                    target_url, new_url)
        elif request.method == "DELETE":
            return_code = self.target_handler.delete_target(target_url)
        else:
            return_code = HttpCode.METH_NOT_ALLOW
        return return_code
