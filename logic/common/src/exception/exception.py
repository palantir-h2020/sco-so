#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from flask import jsonify
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from enum import Enum
from werkzeug.exceptions import HTTPException


class ExceptionCode(Enum):

    BAD_REQUEST = "Bad request"
    IMPROPER_USAGE = "Improper usage"
    INTERNAL_ERROR = "Internal server error"
    INVALID_CONTENT_TYPE = "Invalid Content-Type"
    NOT_FOUND = "Method not found"
    NOT_IMPLEMENTED = "Method not implemented"

    def __get__(self, *args, **kwargs) -> str:
        return self.value

    def __str__(self) -> str:
        return str(self.value)


class SOException:

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
