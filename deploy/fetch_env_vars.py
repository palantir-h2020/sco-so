#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from dict_parse import load_dict
import sys


def load_env_vars_from_yaml(file_name, mappings):
    # Load manually instead of using pyyaml to circumvent
    # installation of extra libraries at the host
    env_vars = []
    dict_contents = load_dict(file_name)
    for env_vars_map_k, env_vars_map_v in mappings.items():
        env_map_k_paths = env_vars_map_k.split(".")
        d_data = dict(dict_contents)
        for env_map_k_path in env_map_k_paths:
            if d_data is not None:
                d_data = d_data.get(env_map_k_path)
        if d_data is not None:
            env_vars.append("{}={}".format(
                env_vars_map_v, d_data))
    return env_vars


def load_modules(file_name, module_name):
    env_vars = []
    dict_contents = load_dict(file_name)
    if dict_contents is not None:
        dict_contents = dict_contents.get("modules", {})
        dict_contents = dict_contents.get(module_name, {})
        env_vars.append("SO_MODL_NAME={}".format(module_name))
        port = dict_contents.get("port")
        if port is not None:
            env_vars.append("SO_MODL_API_PORT={}".format(port))
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
        "db.user": "SO_MODL_DB_USER",
        "db.password": "SO_MODL_DB_USERPASSWORD",
    }
    env_vars += load_env_vars_from_yaml("db.yaml", env_vars_mappings)

    # AAC
    env_vars_mappings = {
        # "keycloak.user": "SO_MODL_AUTH_USER",
        # "keycloak.password": "SO_MODL_AUTH_USERPASSWORD",
        "keycloak.admin-user": "SO_MODL_AUTH_ADMIN_USER",
        "keycloak.admin-password": "SO_MODL_AUTH_ADMIN_USERPASSWORD",
        "db.user": "SO_MODL_AUTH_DB_USER",
        "db.password": "SO_MODL_AUTH_DB_USERPASSWORD",
    }
    env_vars += load_env_vars_from_yaml("aac.yaml", env_vars_mappings)

    return " ".join(env_vars)


if __name__ == "__main__":
    print(fetch_env())
