#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from fastapi import Response
from fastapi.responses import \
    JSONResponse, PlainTextResponse
from common.server.http import content
from common.server.http.content import AllowedContentTypes
from common.server.http.content import error_on_unallowed_method
from common.server.http.http_code import HttpCode
import json
import yaml


class HttpResponse:

    """
    Return specifically encoded responses.
    For more details, check
    - https://github.com/encode/starlette/blob/master/starlette/status.py
    - https://fastapi.tiangolo.com/advanced/custom-response/
    """

    @staticmethod
    def json(status_code: int, status_msg) -> JSONResponse:
        status_msg = content.convert_to_json(status_msg)
        return JSONResponse(status_code=status_code,
                            content=status_msg)

    @staticmethod
    def text(status_code: int, status_msg: str) -> PlainTextResponse:
        return PlainTextResponse(content=status_msg,
                                 status_code=status_code)

    @staticmethod
    def yaml(status_code: int, status_msg) -> Response:
        status_msg = content.convert_to_yaml(status_msg)
        ct = content.AllowedContentTypes.CONTENT_TYPE_YAML
        return Response(content=status_msg,
                        status_code=status_code,
                        media_type=ct)

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
                AllowedContentTypes.CONTENT_TYPE_YAML.value]
        content_type_is_expected = any([ct for ct in map(
            lambda x: ct_accept in x, expected_ct)])
        if not content_type_is_expected:
            return error_on_unallowed_method("Content-Type not expected")
        # Output will be JSON by default
        output = json.dumps(data)
        if "yaml" in ct_accept:
            output = yaml.dump(data, allow_unicode=True)
        return Response(content=output, status_code=status,
                        media_type=content.AllowedContentTypes.
                        CONTENT_TYPE_TEXT.value)
