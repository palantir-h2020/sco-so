#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


# import logging as log
import os
import sys

# logger = log.getLogger("config-parser")


class BaseParser:

    def __init__(self, path: str):
        """
        Constructor. Reads and parses every setting defined in a config file.

        @param path name of the configuration file
        @throws Exception when configuration directive is wrongly processed
        """
        self.settings = {}
        self.path = os.path.abspath(os.path.join(os.path.split(
            os.path.abspath(__file__))[0], "../../../cfg", path))

    def get(self, key: str) -> str:
        """
        Access internal dictionary and retrieve value from given key.

        @param key dictionary key to access
        @return value for desired key
        """
        value = self.__dict__.get(key, None)
        if any(map(
            lambda x: key.endswith(x), [".ini", ".json", ".yaml", ".yml"])) \
                and not value:
            exc_det = "Error retrieving configuration. Missing " + \
                "file {}/{}".format(self.path, key)
            # logger.critical(exc_det)
            sys.exit(exc_det)
        return value
