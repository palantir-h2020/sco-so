#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from dict_parse import load_dict
import json
import sys


def dict_keys_to_list(keys_list, last_key="", ret=[]):
    if len(keys_list) == 0:
        return ret
    for keys_list_i in keys_list:
        if isinstance(keys_list_i, str):
            if len(keys_list[1:]) > 0:
                return dict_keys_to_list(
                        keys_list[1:],
                        keys_list_i,
                        ret
                )
        elif isinstance(keys_list_i, dict):
            for key_k, key_v in keys_list_i.items():
                key_hierarchy = "{}.{}".format(last_key, key_k)
                if isinstance(key_v, str):
                    ret.append(key_hierarchy)
                if isinstance(key_v, dict):
                    ret += dict_keys_to_list(
                            [key_v],
                            key_hierarchy,
                            []
                    )
    return ret


def cfg_load(cfg_file_name):
    cfg = load_dict(cfg_file_name)
    cfg_list = []
    for cfg_item in cfg.items():
        cfg_list.append(cfg_item[0])
        cfg_list.append(cfg_item[1:][0])
    cfg_list = dict_keys_to_list(cfg_list, "", [])
    return set(cfg_list)


def cfg_diff():
    if len(sys.argv) > 1:
        module_name = sys.argv[1]
    else:
        return

    cfg_old_set = cfg_load(module_name)
    cfg_new_set = cfg_load("{}.sample".format(module_name))
    added_keys = []
    removed_keys = []
    # Only provide diff if both files are present
    if len(cfg_old_set) > 0 and len(cfg_new_set) > 0:
        added_keys = list(cfg_new_set - cfg_old_set)
        removed_keys = list(cfg_old_set - cfg_new_set)
    cfg_diff = {
        "added-keys": added_keys,
        "removed-keys": removed_keys,
    }
    return json.dumps(cfg_diff)


if __name__ == "__main__":
    print(cfg_diff())
    # diff_sample_vs_cfg = cfg_diff()
    # if len(diff_sample_vs_cfg.get("added-keys") > 0:
    #     exception_desc = "Could not parse YAML configuration file '%s'. \
    #         Details: %s" % (str(cfg_reader.path), str(e))
    #     sys.exit(exception_desc)
