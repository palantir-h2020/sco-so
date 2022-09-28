#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.config.modules.module_catalogue import ModuleCatalogue
import sys


def fetch_env():
    env_vars = []
    module_catalogue = ModuleCatalogue().modules()
    if len(sys.argv) > 0:
        module_name = sys.argv[1]
    env_vars.append("SO_MODL_NAME={}".format(module_name))
    module_port = module_catalogue.get(module_name, {}).get("port")
    env_vars.append("SO_MODL_API_PORT={}".format(module_port))
    cfg_reader = FullConfParser()
    db_category = cfg_reader.get("db.yaml")
    db_db = db_category.get("db")
    db_user = db_db.get("user")
    db_password = db_db.get("password")
    env_vars.append("SO_MODL_DB_USER={}".format(db_user))
    env_vars.append("SO_MODL_DB_USERPASSWORD={}".format(db_password))
    module_catalogue = ModuleCatalogue().modules()
    return " ".join(env_vars)


if __name__ == "__main__":
    print(fetch_env())
