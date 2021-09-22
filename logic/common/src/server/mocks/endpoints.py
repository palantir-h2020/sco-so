#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from core import regex
from schema import And
from schema import Schema
from schema import Use


class MockEndpoints:

    def __init__(self):
        self.get_api_endpoints_mock = {
            "endpoints":
                [
                    {
                        "methods": ["GET"],
                        "endpoint": "/",
                    },
                    {
                        "methods": ["POST"],
                        "endpoint": "/path/to/post/<vnf_id>",
                    },
                ]
        }

    def get_api_endpoints_schema(self):
        schema = self.get_api_endpoints_mock
        for schema_ep in schema.get("endpoints"):
            schema_ep["methods"] = \
                And(list, lambda l: all(
                    x in ["GET", "POST", "DELETE", "PUT"] for x in l))
            schema_ep["endpoint"] = \
                And(Use(str), lambda n: regex.unix_path(n) is not None)
        return Schema(schema)
