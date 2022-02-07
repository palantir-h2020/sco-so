#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from common.server.http import content
from common.server.http.http_code import HttpCode
from typing import Union
import json


class OSMResponseParsing:
    """
    Terrible hack. Simplify as needed or remove.
    """

    @staticmethod
    def parse_normal(response, result_ct_type: str):
        result = None
        try:
            result = response.json()
        except Exception:
            pass
        try:
            result = response.text
        except Exception:
            pass
        try:
            result = response.response
        except Exception:
            pass
        try:
            result = response.get("response")
        except Exception:
            pass
        if isinstance(result, list) and len(result) == 1:
            result = result[0]
        try:
            result = result.decode("ascii")
        except Exception:
            pass
        try:
            if isinstance(result, dict):
                result = result.get("output")
            if isinstance(result, str):
                result = json.loads(result)
        except Exception:
            pass
        if result is None:
            result = response
        return content.convert_to_ct(result, result_ct_type)

    @staticmethod
    def parse_failed(response) -> Union[dict, str]:
        res_details = response
        try:
            res_details = response._content
        except Exception:
            pass
        try:
            res_details = response.json()
        except Exception:
            pass
        if isinstance(res_details, bytes):
            res_details = res_details.decode("ascii")
        if isinstance(res_details, str):
            try:
                res_details = json.loads(res_details)
            except Exception:
                res_details = str(res_details)
        return res_details

    @staticmethod
    def parse_exception(exc: Exception) -> dict:
        exc_ret = {}
        e_msg = exc.__str__().replace("'", "\"")
        exc_ret = {
            "detail": e_msg,
            "status-code": HttpCode.INTERNAL_ERROR
        }
        try:
            e_msg = json.loads(e_msg)
            exc_ret["status-code"] = e_msg.get("status")
            exc_ret["detail"] = e_msg.get("detail")
        except Exception:
            pass
        return exc_ret

    @staticmethod
    def parse_generic(response, ct_accept: str) -> str:
        status_code = response.status_code
        if status_code is None:
            status_code = HttpCode.INTERNAL_ERROR.value
        result_ct = OSMResponseParsing.parse_failed(response)
        if isinstance(result_ct, dict):
            result_ct = result_ct.get("output", result_ct)
        ret_data = dict()
        ret_data.update({
            "content-type": ct_accept,
            "status-code": status_code
        })
        try:
            response = OSMResponseParsing.parse_normal(
                       response, ct_accept)
            if isinstance(response, dict):
                if "output" in response.keys():
                    response = response.get("output")
                # If provided content is a string, it might be an encoded JSON
                if isinstance(response, str):
                    try:
                        response = json.loads(response)
                    except Exception:
                        pass
            ret_data.update({
                "response": response,
                "content-type": ct_accept
            })
        except Exception as e:
            ret_data.update({
                "output": result_ct,
                "internal-error": str(e)
            })
        return ret_data
