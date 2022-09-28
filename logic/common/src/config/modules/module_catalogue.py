#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common.config.parser.fullparser import FullConfParser


class ModuleCatalogue:
    """
    Retrieve the details for the different modules belonging to SCO/SO.
    This is useful for both the API and to retrieve connection details
    # to other services.
    """

    def __init__(self):
        self.config = FullConfParser()
        self.catalogue_modules = self.config.get("modules.yaml")
        self.catalogue_module = self.catalogue_modules.get("modules")
        self.modules_list = {}
        for cat_name, cat_cfg in self.catalogue_module.items():
            cat_dict = {
                "name": cat_name
            }
            cat_dict.update(cat_cfg)
            self.modules_list[cat_name] = cat_dict

    def modules(self):
        return self.modules_list
