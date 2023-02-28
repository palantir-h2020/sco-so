#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from flask import jsonify
from common.server.http.content import AllowedContentTypes
from common.server.http.http_code import HttpCode
try:
    from common.server.http.http_response_fastapi import HttpResponse
except Exception:
    from common.server.http.http_response import HttpResponse
from common.utils.osm_response_parsing import OSMResponseParsing
from enum import Enum
from functools import wraps
from requests.models import Response
from requests.exceptions import ConnectionError
from werkzeug.exceptions import HTTPException
import re


def handle_exc_resp(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ct_accept = AllowedContentTypes.CONTENT_TYPE_JSON.value
            status = HttpCode.OK
            result = func(*args, **kwargs)
            if "Response" in str(type(result)):
                # FastAPI (default)
                if isinstance(result, Response):
                    status = result.status_code
                    result = result._content
                    if isinstance(result, bytes):
                        result = result.decode("ascii")
                # Flask (consider removing or deleting)
                else:
                    ct_accept = result.content_type
                    status = result.status_code
                    result = result.response
                    if isinstance(result, bytes):
                        result = result.decode("ascii")
                    if ct_accept == AllowedContentTypes\
                        .CONTENT_TYPE_YAML.value and\
                            isinstance(result, list) and len(result) == 1:
                        result = result[0]
                        if isinstance(result, bytes):
                            result = result.decode("ascii")
                        result = [result]
            else:
                try:
                    status = result.get("status")
                    # Remove the status flag upon its processing
                    result.pop("status", None)
                except Exception:
                    pass
            # In case of some internal component returning HTTP 204
            # ("NO CONTENT") but elsewhere some content is emitted,
            # content has priority and the HTTP code is adjusted
            if status == 204 and len(result) > 0:
                status = HttpCode.ACCEPTED
            # return HttpResponse.json(status, result)
            return HttpResponse.infer(result, status, ct_accept)
        except ConnectionError as e:
            e_msg = str(e)
            final_msg = "Network timeout. Details: {}".format(e_msg)
            try:
                re_groups = re.match(
                    ".*HTTPConnectionPool\(host='(.*)', port=(.*)\):.*", e_msg)
                re_groups_len = len(re_groups.groups())
                if re_groups_len > 1:
                    host = re_groups.group(1)
                    port = re_groups.group(2)
                    final_msg = "Network timeout to host={}, port={}".format(
                        host, port) + ". Ensure the service is up"
            except Exception:
                pass
            return HttpResponse.infer(
                {"error": final_msg},
                HttpCode.NET_CONN_TIMEOUT)
        except Exception as e:
            parsed_result, status = OSMResponseParsing.parse_exception(e)
            return HttpResponse.infer(parsed_result, status)
    return wrapper


class ExceptionCode(Enum):

    BAD_REQUEST = "Bad request"
    CONFLICT = "Conflict"
    IMPROPER_USAGE = "Improper usage"
    INTERNAL_ERROR = "Internal server error"
    INVALID_CONTENT_TYPE = "Invalid Content-Type"
    NET_CONN_TIMEOUT = "Network connection error"
    NOT_FOUND = "Method not found"
    NOT_IMPLEMENTED = "Method not implemented"

    def __get__(self, *args, **kwargs) -> str:
        return self.value

    def __str__(self) -> str:
        return str(self.value)


class SOException(Exception):

    @staticmethod
    def abort(error_code: int, error_msg: str,
              error_det: str = None) -> HTTPException:
        response = SOException.inform(error_code, error_msg, error_det)
        raise HTTPException(response=response)

    @staticmethod
    def inform(error_code: int, error_msg: str,
               error_det: str = None) -> HttpResponse:
        error_details = "{0}: {1}".format(error_code, error_msg)
        error = {"error": error_details}
        if error_det is not None:
            error.update({"reason": str(error_det)})
        error = jsonify(error).response
        if len(error) > 0:
            error = error[0]
        return HttpResponse.json(error_code, error)

    @staticmethod
    def bad_request(error_msg: str = None) -> HttpResponse:
        return SOException.inform(
            HttpCode.BAD_REQUEST,
            ExceptionCode.BAD_REQUEST,
            error_msg)

    @staticmethod
    def conflict_from_client(error_msg: str = None) -> HTTPException:
        return SOException.abort(
            HttpCode.CONFLICT,
            ExceptionCode.CONFLICT,
            error_msg)

    @staticmethod
    def improper_usage(error_msg: str = None) -> HTTPException:
        return SOException.abort(
            HttpCode.TEAPOT,
            ExceptionCode.IMPROPER_USAGE,
            error_msg)

    @staticmethod
    def internal_error(error_msg: str = None) -> HTTPException:
        return SOException.abort(
            HttpCode.INTERNAL_ERROR,
            ExceptionCode.INTERNAL_ERROR,
            error_msg)

    @staticmethod
    def network_connection_error(error_msg: str = None) -> HTTPException:
        return SOException.abort(
            HttpCode.NET_CONN_TIMEOUT,
            ExceptionCode.NET_CONN_TIMEOUT,
            error_msg)

    @staticmethod
    def invalid_content_type(error_msg: str = None) -> HTTPException:
        return SOException.abort(
            HttpCode.UNSUP_MEDIA,
            ExceptionCode.INVALID_CONTENT_TYPE,
            error_msg)

    @staticmethod
    def not_implemented(error_msg: str = None) -> HTTPException:
        return SOException.abort(
            HttpCode.NOT_IMPL,
            ExceptionCode.NOT_IMPLEMENTED,
            error_msg)

    @staticmethod
    def not_found(error_msg: str = None) -> HttpResponse:
        return SOException.inform(
            HttpCode.NOT_FOUND,
            ExceptionCode.NOT_FOUND,
            error_msg)

    @staticmethod
    def config_parsing_error(error_msg: str = None):
        raise SOException("Bad configuration. {}".format(error_msg))


class SONotFoundException(SOException):
    def __init__(self, message):
        self.msg = message
        super().__init__(message)


class SONetworkConnectionException(SOException):
    def __init__(self, message):
        self.msg = message
        super().__init__(message)


# TODO Use consistently w.r.t. others
class SOConfigException(SOException):
    def __init__(self, message):
        self.msg = message
        super().__init__(message)
        # super().__init__("Configuration issue. {}".format(message))
