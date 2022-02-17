#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from .baseparser import BaseParser
from .confparser import IniParser
from .jsonparser import JsonParser
from .yamlparser import YamlParser
from common.exception.exception import SOConfigException
import logging as log
import os

logger = log.getLogger("config-parser")


class FullConfParser(BaseParser):

    def __init__(self):
        BaseParser.__init__(self, "")
        self.__load_files()

    def __load_files(self):
        """
        Derives the configuration to a specific parser, based on
        the type of file.
        """
        for f in os.listdir(self.path):
            try:
                if f.endswith(".ini"):
                    self.__dict__.update({str(f): IniParser(f).settings})
                elif f.endswith(".json"):
                    self.__dict__.update({str(f): JsonParser(f).settings})
                elif f.endswith(".yaml") or f.endswith(".yml"):
                    self.__dict__.update({str(f): YamlParser(f).settings})
            except TypeError:
                abspath_cfg_file = os.path.abspath(os.path.join(self.path, f))
                raise SOConfigException(
                        "File {} has improper content".format(
                            abspath_cfg_file))
