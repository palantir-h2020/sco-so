#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from fastapi import Response
from fastapi.responses import \
    JSONResponse, PlainTextResponse
from common.server.http import content
from common.server.http.http_code import HttpCode


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
    def infer(data, headers: dict = {},
              status_code: int = HttpCode.OK) -> Response:
        """
        Format data to be output, based on the expected content_type.
        """
        try:
            return HttpResponse.yaml(status_code, data)
        except Exception:
            pass
        try:
            return HttpResponse.json(status_code, data)
        except Exception:
            pass
        try:
            return HttpResponse.text(status_code, data)
        except Exception:
            pass
        return Response(content=data, status_code=status_code,
                        media_type=content.AllowedContentTypes.
                        CONTENT_TYPE_TEXT)
