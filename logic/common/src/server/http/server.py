#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))

from flask import Blueprint
from common.server.http.server_cfg import ServerConfig
from werkzeug import serving

import importlib
import logging as log
import ssl

logger = log.getLogger("httpserver")

logger.info("server.py, antes de la class Server")

class Server(object):
    """
    Encapsulates a Flask server instance to expose a REST API.
    """
    def __init__(self):
        """
        Constructor for the server wrapper.
        """
        logger.info("server.py, class Server, init")
        cfg = ServerConfig()
        self.__dict__.update(cfg.__dict__)
        self.__load__blueprint_modules()

    def __load__blueprint_modules(self):
        # Load from relative path (in the same folder as current file)
        # blueprints_path = os.path.normpath(os.path.join(
        #             os.path.dirname(__file__), "blueprints"))
        # Load from relative path (in same folder as main.py - entry point)
        logger.info("server.py, class Server, load blueprint")
        blueprints_path = os.path.normpath(os.path.join(".", "blueprints"))
        blueprint_elems = []
        if os.path.isdir(blueprints_path):
            blueprint_elems = filter(
                    lambda x: "__" not in x and x.endswith(".py"),
                    os.listdir(blueprints_path))
        self.blueprints = dict()
        for blueprint_elem in blueprint_elems:
            mod_name = blueprint_elem.replace(".py", "")
            self.blueprints[mod_name] = importlib.import_module(
                    "blueprints." + mod_name)

    @property
    def app(self):
        """
        Returns the flask instance (not part of the service interface,
        since it is specific to flask).
        """
        logger.info("server.py, class Server, app")
        return self._app

    def add_routes(self):
        """
        New method. Allows registering URLs from the blueprint files defined
        under the "blueprints" folder, in the same directory as this file.
        """
        logger.info("server.py, class Server, add_routes")
        for mod_name in self.blueprints.keys():
            if mod_name not in sys.modules:
                loaded_mod = __import__("blueprints" + "." + mod_name,
                                        fromlist=[mod_name])
                for obj in vars(loaded_mod).values():
                    if isinstance(obj, Blueprint):
                        self._app.register_blueprint(obj)

    def run(self):
        """
        Starts up the server. It (will) support different config options
        via the config plugin.
        """
        print("server.py, class Server, run")
        self.add_routes()
        logger.info("Registering app server at %s:%i" % (self.host, self.port))
        try:
            context = None
            if self.https_enabled:
                # Set up a TLS context
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                certs_path = os.path.normpath(os.path.join(
                    os.path.dirname(__file__), "../../../", "cert"))
                context_crt = os.path.join(certs_path, "server.crt")
                context_key = os.path.join(certs_path, "server.key")
                try:
                    context.load_cert_chain(context_crt, context_key)
                except Exception:
                    exc_det = "Error starting server. Missing " + \
                        "server cert or key under {}".format(certs_path)
                    logger.critical(exc_det)
                    sys.exit(exc_det)

                if self.verify_users:
                    context.verify_mode = ssl.CERT_REQUIRED
                    try:
                        context.load_verify_locations(
                            os.path.join(certs_path, "ca.crt"))
                    except Exception:
                        exc_det = "Error starting server. Missing " + \
                            "or empty {}/ca.crt".format(certs_path)
                        logger.critical(exc_det)
                        sys.exit(exc_det)

                    if self.debug:
                        logger.debug("SSL context defined")
                else:
                    if self.debug:
                        logger.debug("SSL context defined with " +
                                     "client verification")

            if self.https_enabled:
                serving.run_simple(
                    self.host, int(self.port), self._app,
                    ssl_context=context, use_reloader=False,
                    threaded=True)
            # No HTTPS required no "ssl_context" object at all
            else:
                serving.run_simple(
                    self.host, int(self.port), self._app,
                    use_reloader=False,
                    threaded=True)
        finally:
            self._app._got_first_request = False
