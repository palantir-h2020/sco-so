#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from common.config.parser.fullparser import FullConfParser


class APICategories:
    """
    Retrieve the endpoints' data for the API.
    """

    def __init__(self):
        self.config = FullConfParser()
        self.api_cat_category = self.config.get("api.categories.yaml")
        self.cat_category = self.api_cat_category.get("categories")
        self.api_categories = {}
        for cat_name, cat_cfg in self.cat_category.items():
            cat_dict = {
                "name": cat_name
            }
            cat_dict.update(cat_cfg)
            self.api_categories[cat_name] = cat_dict

    def categories(self):
        return self.api_categories
