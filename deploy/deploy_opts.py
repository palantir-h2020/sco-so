#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.config.modules.module_catalogue import ModuleCatalogue
import sys


def fetch_env():
    if len(sys.argv) > 0:
        module_name = sys.argv[1]
    else:
        return

    env_vars = []
    module_catalogue = ModuleCatalogue().modules()

    # Current module name and port
    env_vars.append("SO_MODL_NAME={}".format(module_name))
    module_port = module_catalogue.get(module_name, {}).get("port")
    env_vars.append("SO_MODL_API_PORT={}".format(module_port))

    # Common DB access
    cfg_reader = FullConfParser()
    db_category = cfg_reader.get("db.yaml")
    db_db = db_category.get("db")
    db_user = db_db.get("user")
    env_vars.append("SO_MODL_DB_USER={}".format(db_user))
    db_password = db_db.get("password")
    env_vars.append("SO_MODL_DB_USERPASSWORD={}".format(db_password))

    # AAC
    aac_category = cfg_reader.get("aac.yaml")
    aac_keycloak = aac_category.get("keycloak")
    # aac_user = aac_keycloak.get("user")
    # env_vars.append("SO_MODL_AUTH_USER={}".format(aac_user))
    # aac_password = aac_keycloak.get("password")
    # env_vars.append("SO_MODL_AUTH_USERPASSWORD={}".format(aac_password))
    aac_admin_user = aac_keycloak.get("admin-user")
    env_vars.append("SO_MODL_AUTH_ADMIN_USER={}".format(aac_admin_user))
    aac_admin_password = aac_keycloak.get("admin-password")
    env_vars.append("SO_MODL_AUTH_ADMIN_USERPASSWORD={}".format(
        aac_admin_password))
    aac_db_keycloak = aac_category.get("db")
    aac_db_user = aac_db_keycloak.get("user")
    env_vars.append("SO_MODL_AUTH_DB_USER={}".format(aac_db_user))
    aac_db_password = aac_db_keycloak.get("password")
    env_vars.append("SO_MODL_AUTH_DB_USERPASSWORD={}".format(aac_db_password))

    return " ".join(env_vars)


if __name__ == "__main__":
    print(fetch_env())
