#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common.server.http.content import AllowedContentTypes
from common.server.http import content
from common.server.http.http_code import HttpCode
# Required while both Flask and FastAPI are in use
try:
    from common.server.http.http_response_fastapi import HttpResponse
except Exception:
    from common.server.http.http_response import HttpResponse
from requests.models import Response as RequestsResponse
from typing import Union
import json


class OSMResponseParsing:
    @staticmethod
    def parse_normal(response, result_type: str):
        # Case for string and dict
        result = response
        # Case for response objects
        try:
            result = response.json()
        except Exception:
            pass
        try:
            result = response.text
        except Exception:
            pass
        return content.convert_to_ct(result, result_type)

    @staticmethod
    def parse_failed(response) -> Union[dict, str]:
        default_status = HttpCode.INTERNAL_ERROR
        status = default_status
        exc_ret = {}
        res_details = response
        try:
            res_details = response._content
            status = response.status_code
        except Exception:
            pass
        if isinstance(res_details, bytes):
            res_details = res_details.decode("ascii")
        if isinstance(res_details, str):
            try:
                res_details = json.loads(res_details)
                # This shall also update the status
                exc_ret.update({"error": res_details.get("error")})
                status = res_details.get("status", status)
            except Exception:
                res_details = str(res_details)
        else:
            exc_ret.update({"error": res_details})
        if status is None:
            status = default_status
        return (exc_ret, status)

    @staticmethod
    def parse_exception(exc: Exception) -> dict:
        exc_ret = {}
        default_status = HttpCode.INTERNAL_ERROR
        status = default_status
        try:
            exc_msg = exc.msg
        except Exception:
            exc_msg = str(exc)
        # Exception with a dictionary including message and status code
        if isinstance(exc_msg, str):
            try:
                exc_msg = exc_msg.replace("'", "\"")
                exc_msg = json.loads(exc_msg)
            except Exception:
                pass
        if isinstance(exc_msg, dict):
            status = exc_msg.get("status", status)
            e_msg = exc_msg.get("error", exc.msg)
        # Exception with simple strings (or encoded dictionaries)
        else:
            try:
                e_msg = json.loads(e_msg)
                status = e_msg.get("status", status)
                exc_ret["detail"] = e_msg.get("error", "No details available")
            except Exception:
                e_msg = str(exc_msg)
                # e_msg = "Unknown error. Possible cause: {}".format(e)
        exc_ret = {
            "error": e_msg,
        }
        if status is None:
            status = default_status
        return (exc_ret, status)

    @staticmethod
    def parse_generic_old(response, ct_accept: str) -> str:
        # Check first for failure (exceptions)
        result, status = OSMResponseParsing.parse_failed(response)
        status = response.status_code
        if status is None:
            status = HttpCode.INTERNAL_ERROR.value
        ret_data = dict()
        ret_data.update({
            "content-type": ct_accept,
            "status": status
        })
        try:
            response = OSMResponseParsing.parse_normal(
                       response, ct_accept)
            if isinstance(response, dict):
                response = response.get("output")
            ret_data.update({
                "response": response,
                "content-type": ct_accept
            })
        except Exception as e:
            ret_data.update({
                "output": result,
                "error": str(e)
            })
        return ret_data

    @staticmethod
    def parse(response, ct_accept: str) -> str:
        default_status = HttpCode.OK
        status = default_status
        result = {}
        response_ct = response
        # Case of response objects
        if isinstance(response, RequestsResponse):
            response_ct = response._content
            status = response.status_code
            # Case of dictionaries encoded in binary or text form
            try:
                if isinstance(response_ct, bytes):
                    response_ct = response_ct.decode("ascii")
                response_ct = json.loads(response_ct)
            except Exception:
                pass
        if ct_accept is None:
            ct_accept = AllowedContentTypes.CONTENT_TYPE_JSON.value
        try:
            if isinstance(response_ct, dict) and "error" in response_ct.keys():
                # Check first for failure (exceptions)
                parsed_f, status = OSMResponseParsing.parse_failed(response)
                result.update({"error": parsed_f.get("error")})
            else:
                # Otherwise provide anything as it is
                result = OSMResponseParsing.parse_normal(response, ct_accept)
        except Exception as e:
            status = HttpCode.INTERNAL_ERROR
            try:
                e_msg = e.msg
            except Exception:
                e_msg = e.__str__()
            result.update({
                "error": str(e_msg)
            })
        if status is None:
            status = default_status
        return (result, status)

    @staticmethod
    def parse_send(response, ct_accept: str) -> str:
        result, status = OSMResponseParsing.parse(response, ct_accept)
        return HttpResponse.infer(result, status, ct_accept)
