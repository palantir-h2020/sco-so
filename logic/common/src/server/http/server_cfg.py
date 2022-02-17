#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.config.parser.fullparser import FullConfParser
from common.exception.exception import SOException
from common.db.manager import DBManager
from flask import Flask
from flask import g
from common.server.http.http_code import HttpCode

import ast
import os

API_HOST = "0.0.0.0"
API_PORT = "50100"
API_DEBUG = True
# FIXME: re-enable
# HTTPS_ENABLED = True
HTTPS_ENABLED = False
API_VERIFY_CLIENT = False


class ServerConfig(object):
    """
    Configuration for the Flask server.
    """

    def __init__(self):
        """
        Constructor for the server wrapper.
        """
        # Imports the named package, in this case this file
        self.__import_config()
        self._app = Flask(
                __name__.split(".")[-1],
                template_folder=self.template_folder)
        self._app.mongo = DBManager()
        # self._app.so_host = self.so_host
        # self._app.so_port = self.so_port
        # Added in order to be able to execute "before_request" method
        app = self._app

        @app.before_request
        def before_request():
            # "Attach" objects within the "g" object.
            # This is passed to each view method
            g.mongo = self._app.mongo

        @app.errorhandler(HttpCode.BAD_REQUEST)
        def bad_request(error):
            return SOException.bad_request(error)

        @app.errorhandler(HttpCode.NOT_FOUND)
        def not_found(error):
            return SOException.not_found(error)

        @app.errorhandler(HttpCode.INTERNAL_ERROR)
        def internal_error(error):
            return SOException.internal_error(error)

    def __import_config(self):
        """
        Fill properties fom configuration files.
        """
        self.config = FullConfParser()
        # Imports API-related info
        self.api_category = self.config.get("api.yaml")
        # General API data
        self.api_general = self.api_category.get("general")
        self.host = self.api_general.get("host", API_HOST)
        self.port = self.api_general.get("port", API_PORT)
        self.debug = ast.literal_eval(
                self.api_general.get("debug")) or API_DEBUG
        # Verification and certificates
        self.api_sec = self.api_category.get("security")
        self.https_enabled = ast.literal_eval(
                self.api_sec.get("https_enabled")) \
            or HTTPS_ENABLED
        self.verify_users = ast.literal_eval(
                self.api_sec.get("verify_client_cert")) \
            or API_VERIFY_CLIENT
        # Performance
        self.api_perf = self.api_category.get("performance")
        self.workers = self.api_perf.get("parallel_workers", 0)
        # GUI data
        self.template_folder = os.path.normpath(
            os.path.join(os.path.dirname(__file__),
                         "../../gui", "flask_swagger_ui/templates"))
        # General NFVO data
        # self.so_category = self.config.get("so.yaml")
        # self.so_general = self.so_category.get("general")
        # self.so_host = self.so_general.get("host")
        # self.so_port = self.so_general.get("port")
