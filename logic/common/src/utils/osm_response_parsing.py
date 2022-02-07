#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from common.server.http import content
from common.server.http.http_code import HttpCode
from typing import Union
import json


class OSMResponseParsing:
    @staticmethod
    def parse_normal(response, result_ct_type: str):
        try:
            response = response.json()
        except Exception:
            response = response.text
        return content.convert_to_ct(response, result_ct_type)

    @staticmethod
    def parse_failed(response) -> Union[dict, str]:
        res_details = response._content
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
                response = response.get("output")
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
