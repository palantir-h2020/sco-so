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
    CONTENT_TYPE_APPGZIP = "application/gzip"
    CONTENT_TYPE_ANY = "*/*"
    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_MULTI = "multipart/form-data"
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
    result = data
    if isinstance(data, bytes):
        result = result.decode("ascii")
    if isinstance(data, str):
        if data.startswith("b'") or data.startswith('b"'):
            result = result[1:]
        try:
            # Replace strings in the form "'{\"k\":\"v\"}'"
            result = result.replace("'", "")
            result = result.replace("\n", "")
            result = result.replace("\\n", "")
            result = json.loads(result)
        except Exception:
            pass
    # return json.dumps(data)
    return result


def convert_to_yaml(data) -> str:
    if isinstance(data, bytes):
        result = result.decode("ascii")
    if isinstance(data, str):
        data = convert_to_json(data)
    if isinstance(data, dict):
        try:
            data = yaml.dump(data, Dumper=YAMLDumper,
                             default_flow_style=False)
        except Exception:
            data = str(data)


def convert_to_ct(data, accept_type: str):
    print(".....................................>")
    print("........ accept_type={}..............>".format(accept_type))
    print(".....................................>")
    # Enforce JSON by default when no specific preferences are provided
    if accept_type == AllowedContentTypes.CONTENT_TYPE_ANY.value:
        accept_type = AllowedContentTypes.CONTENT_TYPE_JSON.value
    if AllowedContentTypes.CONTENT_TYPE_YAML.value in accept_type:
        return convert_to_yaml(data)
    elif any(map(lambda x: x in accept_type,
            [AllowedContentTypes.CONTENT_TYPE_JSON.value,
             AllowedContentTypes.CONTENT_TYPE_TEXT.value])):
        return data
    else:
        raise Exception("Unsupported or non-existing " +
                        "Accept-Type: {}".format(accept_type))
