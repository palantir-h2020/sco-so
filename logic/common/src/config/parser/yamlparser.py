#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from .baseparser import BaseParser
import yaml
import logging as log
import sys

logger = log.getLogger("config-parser")


class YamlParser(BaseParser):

    def __init__(self, path: str):
        """
        Constructor. Reads the YAML config file.

        @param path name of the configuration file
        @throws Exception when configuration directive is wrongly processed
        """
        BaseParser.__init__(self, path)
        try:
            with open(self.path) as data_file:
                self.settings = yaml.safe_load(data_file)
        except Exception as e:
            exception_desc = "Could not parse YAML configuration file '%s'. \
                Details: %s" % (str(self.path), str(e))
            logger.exception(exception_desc)
            sys.exit(exception_desc)
        self.__dict__.update(self.settings)
