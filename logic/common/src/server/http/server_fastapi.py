#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))
from common.config.modules.module_catalogue import ModuleCatalogue
from common.server.http.server_cfg import ServerConfig
from fastapi import FastAPI
from fastapi.routing import APIRouter
import importlib
import logging as log
# import ssl
import uvicorn


logger = log.getLogger("httpserver")


class Settings:
    def __init__(self):
        self.api_version = "v1"
        self.api_name = "my_api"
        self.db = "some db"
        self.logger = "configured logger"
        self.DEBUG = True


class ExternalAPI:
    def __init__(self, settings):
        self.settings = settings
        self.fastapi = FastAPI(
                        title="SCO/SO API",
                        description="API endpoints for SCO/SO",
                        docs_url="/api/docs",
                        redoc_url=None,
                        version=self.settings.api_version,
                        contact={
                            "name": "Carolina Fernandez",
                            "email": "carolina.fernandez@i2cat.net",
                        },
                       )


app = ExternalAPI(Settings()).fastapi


class Server:
    """
    Encapsulates a FastAPI server instance to expose a REST API.
    """

    def __init__(self):
        cfg = ServerConfig()
        # self.port = int(os.environ.get("SO_MODL_API_PORT"))
        self.__dict__.update(cfg.__dict__)
        self.__load__blueprint_modules()
        self.settings = Settings()
        # self.app = ExternalAPI(self.settings)
        self.module_catalogue = ModuleCatalogue().modules()

    def __load__blueprint_modules(self):
        # TODO: integrate with behaviour in server.py (move all to FastAPI)
        # Load from relative path (in the same folder as current file)
        # blueprints_path = os.path.normpath(os.path.join(
        #             os.path.dirname(__file__), "blueprints"))
        # Load from relative path (in same folder as the main.py entry point)
        blueprints_path = os.path.normpath(os.path.join(".", "blueprints"))
        blueprint_elems = []
        if os.path.isdir(blueprints_path):
            blueprint_elems = filter(
                    lambda x: "__" not in x and x.endswith(".py"),
                    os.listdir(blueprints_path))
        self.blueprints = dict()
        for blueprint_elem in blueprint_elems:
            mod_name = blueprint_elem.replace(".py", "")
            # CF: added to filter non-FastAPI modules (to be integrated
            # with server.py behaviour in the future -> all moved to FastAPI)
            if mod_name.endswith("_fastapi"):
                self.blueprints[mod_name] = importlib.import_module(
                        "blueprints." + mod_name)

    def add_routes(self):
        """
        On-the-fly registration of URLs from the blueprint/router
        files defined under the "blueprints" folder, in the same
        directory as this file.
        """
        for mod_name in self.blueprints.keys():
            if mod_name not in sys.modules:
                loaded_mod = __import__(
                        "blueprints" + "." + mod_name,
                        fromlist=[mod_name])
                # The module name will follow this scheme:
                # "api_<module>_fastapi", where the name of the module will
                # be used to identify the prefix
                try:
                    mod_type = ""
                    mod_type = mod_name.split("_")[1]
                    # CF: using "base" as synonym for "/"
                    if mod_type == "base":
                        mod_type = ""
                    # Note: the endpoint prefix must start with "/"
                    mod_prefix = "/{}".format(mod_type)
                    for obj in vars(loaded_mod).values():
                        if isinstance(obj, APIRouter):
                            if mod_prefix == "/":
                                # app.include_router(obj, tags=["API"])
                                pass
                            else:
                                mod_title = self.module_catalogue.get(
                                        mod_type, mod_type)
                                if isinstance(mod_title, dict):
                                    mod_title = mod_title.get("title", "")
                                app.include_router(obj, prefix=mod_prefix,
                                                   tags=[mod_title])
                except Exception as e:
                    raise Exception("Cannot fetch endpoint from imported\
                                     blueprint: {}.Details: {}".format(
                                         mod_name, str(e)))

    def run(self):
        """
        Starts up the server.
        """
        self.add_routes()
        logger.info("Registering app server at %s:%i", self.host, self.port)

        server_settings = {
            "host": self.host,
            "port": self.port,
            # "reload": False
        }
        if self.workers > 1:
            server_settings.update({
                "workers": self.workers
            })
            raise Exception(
                "Cannot support multiple server workers. Check " +
                "cfg/api.yaml and set these in the range: [0,1]")

        if self.https_enabled:
            try:
                self.certs_path = os.path.normpath(os.path.join(
                    os.path.dirname(__file__), "../../../", "cert"))
            except Exception as e:
                raise Exception("Cannot reach directory with SSL \
                        data. Details: {}".format(e))
            self.ssl_cert_path = os.path.join(self.certs_path, "server.crt")
            self.ssl_key_path = os.path.join(self.certs_path, "server.key")
            server_settings.update({
                "ssl_certfile": self.ssl_cert_path,
                "ssl_keyfile": self.ssl_key_path
            })
            if self.verify_users:
                self.ssl_ca_path = os.path.join(self.certs_path, "ca.crt")
                server_settings.update({
                    "ssl_ca_certs": self.ssl_ca_path
                })

        srv_app = app
        if any(map(lambda x: x in server_settings.keys(),
               ["workers", "reload"])):
            # Running uvicorn with "workers" or "reload" require
            # pointing to the "app" object using a string
            srv_app = "common.server.http.server_fastapi:app"
        uvicorn.run(srv_app, **server_settings)

#        if self.https_enabled:
#            if self.verify_users:
#                self.ssl_ca_path = os.path.join(self.certs_path, "ca.crt")
#                uvicorn.run(app, host=self.host, port=self.port,
#                            ssl_certfile=self.ssl_cert_path,
#                            ssl_keyfile=self.ssl_key_path,
#                            ssl_ca_certs=self.ssl_ca_path)
#            else:
#                uvicorn.run(app, host=self.host, port=self.port,
#                            ssl_certfile=self.ssl_cert_path,
#                            ssl_keyfile=self.ssl_key_path)
#        else:
#            # uvicorn.run("common.server.http.server_fastapi:app",
#            #             host=self.host, port=self.port,
#            #             workers=4, reload=False)
#            uvicorn.run(app, host=self.host, port=self.port)


if __name__ == "__main__":
    Server().run()
