#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from .baseparser import BaseParser
try:
    from StringIO import StringIO
    import ConfigParser
except ImportError:
    from io import StringIO
    from configparser import ConfigParser
import logging as log
import sys

logger = log.getLogger("config-parser")


class IniParser(BaseParser):

    def __init__(self, path: str):
        """
        Constructor. Reads and parses every setting defined in a config file.

        @param path name of the configuration file
        @throws Exception when configuration directive is wrongly processed
        """
        BaseParser.__init__(self, path)
        try:
            try:
                confparser = ConfigParser.SafeConfigParser()
            except AttributeError:
                confparser = ConfigParser()
            # Parse data previously to ignore tabs, spaces or others
            conf_data = StringIO("\n".join(
                line.strip() for line in open(self.path)))
            parse_ok = True
            try:
                confparser.readfp(conf_data)
            # Error reading: eg. bad value substitution (bad format in strings)
            except ConfigParser.InterpolationMissingOptionError:
                confparser.read(conf_data)
                parse_ok = False
            # Do some post-processing of the conf sections
            self.__process_conf_sections(confparser, parse_ok)
        except Exception as e:
            exception_desc = "Could not parse configuration file '%s'. Details:\
                %s" % (str(self.path), str(e))
            logger.exception(exception_desc)
            sys.exit(exception_desc)
        self.__dict__.update(self.settings)

    def __process_conf_sections(self, confparser: ConfigParser,
                                parse_ok: bool = True):
        """
        Parses every setting defined in a config file.

        @param confparser ConfigParser object
        @param parse_ok   flag indicating the current parsing status
        @throws Exception when configuration directive is wrongly processed
        """
        for section in confparser.sections():
            self.settings[section] = {}
            try:
                confparser_items = confparser.items(section)
            except Exception:
                confparser_items = confparser._sections.items()
                parse_ok = False
            for (key, val) in confparser_items:
                if parse_ok:
                    if key == "topics":
                        try:
                            val = [v.strip() for v in val.split(",")]
                        except Exception:
                            exception_desc = "Could not process topics: \
                                %s" % str(val)
                            logger.exception(exception_desc)
                            sys.exit(exception_desc)
                    self.settings[section][key] = val
                else:
                    try:
                        for v in val.items():
                            if v[0] != "__name__":
                                self.settings[section][v[0]] = \
                                    str(v[1]).replace('\"', '')
                    except Exception as e:
                        exception_desc = "Cannot process item: %s. \
                            Details: %s" % str(val, e)
                        logger.exception(exception_desc)
                        sys.exit(exception_desc)
