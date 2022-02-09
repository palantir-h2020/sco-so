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
from requests.models import Response as RequestsResponse
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
    def infer_REMOVE(data, status: int = HttpCode.OK,
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

    @staticmethod
    def infer(data, status: int = HttpCode.OK,
              ct_accept: str = None) -> Response:
        """
        Format data to be output, based on the expected content_type.
        """
        if ct_accept is None or ct_accept == "*/*":
            ct_accept = AllowedContentTypes.CONTENT_TYPE_JSON.value
        expected_ct = [
                AllowedContentTypes.CONTENT_TYPE_APPGZIP.value,
                AllowedContentTypes.CONTENT_TYPE_JSON.value,
                AllowedContentTypes.CONTENT_TYPE_MULTI.value,
                AllowedContentTypes.CONTENT_TYPE_YAML.value,
                AllowedContentTypes.CONTENT_TYPE_TEXT.value]
        content_type_is_expected = any(map(
            lambda x: x in ct_accept, expected_ct))
        print("INFER -> ct_accept: " + str(ct_accept))
        print("INFER -> expected_ct: " + str(expected_ct))
        print("content_type_is_expected: " + str(content_type_is_expected))
        if not content_type_is_expected:
            print("INFER -> RAISING ERROR!")
            return error_on_unallowed_method(
                "Content-Type not expected: {}".format(ct_accept))
        print("777777777777777777777777777777777777777777777777777777777777")
        #print(data.__dict__)
        print(type(data))
        print("777777777777777777777777777777777777777777777777777777777777")
        output = data
        # Output will be JSON by default
        if isinstance(data, RequestsResponse):
            print("(((((((((((((((((((( IS INSTANCE OF RESPONSE)))))))))))))))))))")
            output = data._content
        elif isinstance(data, dict):
            if AllowedContentTypes.CONTENT_TYPE_JSON.value in ct_accept:
                try:
                    print(type(data))
                    print(data)
                    #output = json.loads(data)
                    output = json.dumps(data)
                except Exception:
                    output = str(data)
        elif isinstance(data, str):
            try:
                print("woooooooooooooooooo1")
                if AllowedContentTypes.CONTENT_TYPE_JSON.value in ct_accept:
                    print("woooooooooooooooooo2")
                    # output = json.loads(data)
                    output = data
                    print("woooooooooooooooooo3")
                elif AllowedContentTypes.CONTENT_TYPE_YAML.value in ct_accept:
                    print("woooooooooooooooooo4")
                    output = yaml.dump(data, allow_unicode=True)
                    print("woooooooooooooooooo5")
            except Exception as e:
                print("woooooooooooooooooo6")
                output = str(data)
                print(e)
        print("type....={}".format(type(output)))
        print("output_={}>".format(output))
        # Line adapted for FastAPI
        #r1 = Response(content=output, status_code=status, media_type=ct_accept)
        #print("-----------------output----------")
        #print(output)
        #print("-----------------r1----------")
        #print(r1.__dict__)
        # Line adapted for FastAPI
        return Response(content=output, status_code=status, media_type=ct_accept)
