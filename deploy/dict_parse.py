#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from common.config.parser.baseparser import BaseParser
import os
import sys
import yaml


def load_dict(file_name):
    cfg_reader = BaseParser(file_name)
    dict_contents = {}
    if not os.path.isfile(cfg_reader.path):
        return dict_contents
    try:
        with open(cfg_reader.path) as data_file:
            dict_contents = yaml.safe_load(data_file)
    except Exception as e:
        exception_desc = "Could not parse YAML configuration file '%s'. \
            Details: %s" % (str(cfg_reader.path), str(e))
        sys.exit(exception_desc)
    return dict_contents


def parse_dict():
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        return
    return load_dict(file_name)


if __name__ == "__main__":
    print(parse_dict())
