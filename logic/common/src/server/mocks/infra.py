#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from schema import And
from schema import Optional
from schema import Schema
from schema import Use

import uuid


class MockInfra:

    def __init__(self):
        self.res_key = "node"
        self.post_node_mock = {
            "node_id": str(uuid.uuid4())
        }

    def post_node_schema(self):
        schema = self.post_node_mock
        schema["node_id"] = And(Use(str))
        return Schema(schema)

    def get_node_schema(self):
        schema = self.post_node_mock
        schema["host_name"] = And(Use(str))
        schema["node_id"] = And(Use(str))
        schema["analysis_type"] = And(Use(str))
        schema["distribution"] = And(Use(str))
        schema["ip_address"] = And(Use(str))
        schema["pcr0"] = And(Use(str))
        schema["status"] = And(Use(str))
        schema["driver"] = And(Use(str))
        schema["timestamp"] = Optional(Use(str))
        schema["configuration"] = Optional(Use(str))
        return Schema(schema)
