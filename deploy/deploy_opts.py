#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from common.config.parser.baseparser import BaseParser
import sys


def load_env_vars_from_yaml(file_name, mappings):
    # Load manually instead of using pyyaml to circumvent
    # installation of extra libraries at the host
    env_vars = []
    cfg_reader = BaseParser(file_name)
    with open(cfg_reader.path, "r") as cfg_reader_data:
        cfg_data = cfg_reader_data.readlines()
        for cfg_data_item in cfg_data:
            try:
                cfg_data_item = cfg_data_item.replace("\n", "")
                cfg_data_item = cfg_data_item.replace(" ", "")
                cfg_data_key, cfg_data_value = cfg_data_item.split(":")
            except Exception:
                cfg_data_key, cfg_data_value = None, None
            if cfg_data_key is not None:
                for cfg_key, env_var in mappings.items():
                    if cfg_key == cfg_data_key:
                        env_vars.append("{}={}".format(
                            env_var, cfg_data_value))
    return env_vars


def load_modules(file_name, module_name):
    env_vars = []
    cfg_reader = BaseParser(file_name)
    module_found = False
    with open(cfg_reader.path, "r") as cfg_reader_data:
        cfg_data = cfg_reader_data.readlines()
        for cfg_data_item in cfg_data:
            try:
                cfg_data_item = cfg_data_item.replace("\n", "")
                cfg_data_item = cfg_data_item.replace(" ", "")
                cfg_data_key, cfg_data_value = cfg_data_item.split(":")
            except Exception:
                cfg_data_key, cfg_data_value = None, None
            if module_name == cfg_data_key:
                # Section is found. Continue until parsing the port
                module_found = True
                env_vars.append("SO_MODL_NAME={}".format(cfg_data_key))
            if module_found and "port" == cfg_data_key:
                env_vars.append("SO_MODL_API_PORT={}".format(cfg_data_value))
                # Once retrieving this value, get out - do not process more
                break
    return env_vars


def fetch_env():
    if len(sys.argv) > 1:
        module_name = sys.argv[1]
    else:
        return

    env_vars = []

    # Current module name and port
    env_vars = load_modules("modules.yaml", module_name)

    # Common DB access
    env_vars_mappings = {
        "user": "SO_MODL_DB_USER",
        "password": "SO_MODL_DB_USERPASSWORD",
    }
    env_vars += load_env_vars_from_yaml("db.yaml", env_vars_mappings)

    # AAC
    env_vars_mappings = {
        # "user": "SO_MODL_AUTH_USER",
        # "password": "SO_MODL_AUTH_USERPASSWORD",
        "admin-user": "SO_MODL_AUTH_ADMIN_USER",
        "admin-password": "SO_MODL_AUTH_ADMIN_USERPASSWORD",
        "user": "SO_MODL_AUTH_DB_USER",
        "password": "SO_MODL_AUTH_DB_USERPASSWORD",
    }
    env_vars += load_env_vars_from_yaml("aac.yaml", env_vars_mappings)

    return " ".join(env_vars)


if __name__ == "__main__":
    print(fetch_env())
