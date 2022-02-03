#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from enum import Enum
from functools import wraps
from flask import request
from flask import Response
import json
import yaml


class AllowedContentTypes(Enum):
    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_TEXT = "text/plain"
    CONTENT_TYPE_YAML = "application/x-yaml"


def data_in_request(request, expected):
    if request.is_json and "application/json" in \
            request.__dict__.get("environ").get("CONTENT_TYPE"):
        return all(map(lambda x: x in request.json.keys(), expected))
    return False


def error_on_unallowed_method(output):
    resp = Response(str(output), status=405, mimetype="text/plain")
    return resp


def expect_given_content(expected_content: str):
    best = request.accept_mimetypes \
        .best_match([expected_content, "text/html"])
    return best == expected_content


def expect_json_content(func):
    """
    Enforce check of Content-Type header to meet 'application/json'.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if expect_given_content("application/json"):
            return func(*args, **kwargs)
        else:
            return error_on_unallowed_method("Content-Type not expected")
    return wrapper


def on_mock(output):
    def on_mock_outer(func):
        """
        Return specific output when mocked, otherwise run function as usual.
        """
        @wraps(func)
        def on_mock_inner(*args, **kwargs):
            if "mock" in kwargs:
                mock = kwargs.pop("mock", False)
                return str(output if mock else {})
            return func(*args, **kwargs)
        return on_mock_inner
    return on_mock_outer


def filter_actions(actions: list):
    filtered = filter(
            lambda x: x in ["GET", "POST", "PUT", "PATCH", "DELETE"],
            actions)
    return [f for f in filtered]


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


class YAMLDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(YAMLDumper, self).increase_indent(flow, False)


def convert_to_json(data) -> dict:
    if isinstance(data, str):
        print("cj-1a")
        try:
            data = json.loads(data)
            print("cj-1b")
        except Exception:
            pass
    elif not isinstance(data, dict):
        print("cj-2a")
        try:
            data = json.dumps(data)
            print("cj-2b")
        except Exception:
            data = str(data)
    return data


def convert_to_yaml(data) -> str:
    if not isinstance(data, str):
        print("cy-1")
        try:
            data = yaml.dump(data, Dumper=YAMLDumper,
                             default_flow_style=False)
            print("cy-2")
            print(data)
        except Exception:
            data = str(data)
    return data


def convert_to_ct(data, content_type: str):
    if "yaml" in content_type:
        return convert_to_yaml(data)
    elif "json" in content_type:
        return data
    else:
        raise Exception("Unsupported or non-existing " +
                        "Content-Type: {}".format(content_type))
