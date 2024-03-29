#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.server.http.content import AllowedContentTypes
from common.server.http.content import error_on_unallowed_method
from common.server.http.http_code import HttpCode
from flask import jsonify
# from flask import request
from flask import Response

import json
import yaml


class HttpResponse:

    @staticmethod
    def set_content_type(content_type: str):
        return {"Content-Type": content_type}

    @staticmethod
    def json(status_code: int, status_msg: str):
        if not isinstance(status_msg, str):
            try:
                status_msg = jsonify(status_msg).response
            except TypeError:
                status_msg = str(status_msg)
        headers = HttpResponse.set_content_type(
            AllowedContentTypes.CONTENT_TYPE_JSON.value)
        return HttpResponse.generic(status_code, status_msg, headers)

    @staticmethod
    def json_unformatted(status_code: int, status_msg: str):
        headers = HttpResponse.set_content_type(
            AllowedContentTypes.CONTENT_TYPE_JSON.value)
        try:
            import json
            status_msg = json.dumps(status_msg)
        except Exception:
            status_msg = str(status_msg)
        return HttpResponse.generic(status_code, status_msg, headers)

    @staticmethod
    def text(status_code: int, status_msg: str):
        headers = HttpResponse.set_content_type(
            AllowedContentTypes.CONTENT_TYPE_TEXT.value)
        return HttpResponse.generic(status_code, status_msg, headers)

    @staticmethod
    def yaml(status_code: int, status_msg: str):
        if not isinstance(status_msg, str):
            try:
                status_msg = yaml.dump(status_msg, allow_unicode=True)
            except TypeError:
                status_msg = str(status_msg)
        headers = HttpResponse.set_content_type(
            AllowedContentTypes.CONTENT_TYPE_YAML.value)
        return HttpResponse.generic(status_code, status_msg, headers)

    @staticmethod
    def generic(status_code: int, status_msg: str, headers):
        return Response(status=status_code, response=status_msg,
                        headers=headers)

    @staticmethod
    def infer(data, status: int = HttpCode.OK,
              ct_accept: str = None) -> Response:
        """
        Format data to be output, based on the expected content_type.
        """
        if ct_accept is None or ct_accept == "*/*":
            ct_accept = AllowedContentTypes.CONTENT_TYPE_JSON.value
        expected_ct = [
                AllowedContentTypes.CONTENT_TYPE_JSON.value,
                AllowedContentTypes.CONTENT_TYPE_YAML.value,
                AllowedContentTypes.CONTENT_TYPE_TEXT.value]
        accept_type_is_expected = any(map(
            lambda x: x in ct_accept, expected_ct))
        if not accept_type_is_expected:
            return error_on_unallowed_method(
                "Accept-Type not expected: {}".format(ct_accept))
        # Output will be JSON by default
        output = json.dumps(data)
        if "yaml" in ct_accept:
            output = yaml.dump(data, allow_unicode=True)
        return Response(output, status=status, mimetype=ct_accept)
