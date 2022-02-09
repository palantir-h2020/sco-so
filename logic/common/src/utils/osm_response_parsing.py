#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from common.server.http.content import AllowedContentTypes
from common.server.http import content
from common.server.http.http_code import HttpCode
# Required while both Flask and FastAPI are in use
try:
    # # # TEST -> import fastapi
    from common.server.http.http_response_fastapi import HttpResponse
except Exception:
    from common.server.http.http_response import HttpResponse
from requests.models import Response as RequestsResponse
from typing import Union
import json


class OSMResponseParsing:
    @staticmethod
    def parse_normal(response, result_type: str):
        print("\n\n\n\n\n\n\n\n\n type response = {}".format(type(response)))
        # print(response.__dict__)
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
        print(result)
        print("\n\n\n\n\n\n\n")
        return content.convert_to_ct(result, result_type)

    @staticmethod
    def parse_failed(response) -> Union[dict, str]:
        print("res_details............. parse_failed")
        default_status = HttpCode.INTERNAL_ERROR
        status = default_status
        exc_ret = {}
        res_details = response
        try:
            print(">.....>")
            print(res_details.__dict__)
            res_details = response._content
            status = response.status_code
            print("\n\n\nstatus 1={}".format(status))
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
                print(res_details)
                print("\n\n\nstatus 2={}".format(status))
            except Exception as e:
                print("exception...{}".format(e))
                res_details = str(res_details)
        else:
            print("------------------------------------------------------------------------------------------ got to the else")
            exc_ret.update({"error": res_details})
        print(">.....>")
        print(exc_ret)
        if status is None:
            status = default_status
        return (exc_ret, status)

    @staticmethod
    def parse_exception(exc: Exception) -> dict:
#        print("res_details............. parse_exception")
#        print(exc)
#        exc_ret = {}
#        default_status = HttpCode.INTERNAL_ERROR
#        e_msg = exc.__str__().replace("'", "\"")
#        exc_ret = {
#            "detail": e_msg,
#            "status": default_status
#        }
#        try:
#            e_msg = json.loads(e_msg)
#            exc_ret["status"] = e_msg.get("status", default_status)
#            exc_ret["detail"] = e_msg.get("detail", "No details available")
#        except Exception:
#            pass
#        return exc_ret
        print("res_details............. parse_exception")
        print(exc)
        print(dir(exc))
        exc_ret = {}
        default_status = HttpCode.INTERNAL_ERROR
        status = default_status
        try:
            exc_msg = exc.msg
        except:
            exc_msg = str(exc)
        print("type .... {}".format(type(exc_msg)))
        # Exception with a dictionary including message and status code
        if isinstance(exc_msg, str):
            try:
                print("dictionary")
                exc_msg = exc_msg.replace("'", "\"")
                exc_msg = json.loads(exc_msg)
            except Exception:
                pass
        if isinstance(exc_msg, dict):
            print("this is a dictionary **** ")
            print(exc_msg)
            status = exc_msg.get("status", status)
            print(status)
            e_msg = exc_msg.get("error", exc.msg) 
            print(e_msg)
            print("...")
        # Exception with simple strings (or encoded dictionaries)
        else:
            try:    
                print("---------------------------------------------- e_msg={} ----------------------------------".format(e_msg))
                e_msg = json.loads(e_msg)
#                e_msg = exc.__str__().replace("'", "\"")
                status = e_msg.get("status", status)
                exc_ret["detail"] = e_msg.get("error", "No details available")
            except Exception as e:
                e_msg = str(exc_msg)
                # e_msg = "Unknown error. Possible cause: {}".format(e)
        exc_ret = {
            "error": e_msg,
#            "status": status
        }
#        return exc_ret
        if status is None:
            status = default_status
        return (exc_ret, status)

#    @staticmethod
#    def parse_successful(response, ct_accept: str) -> str:
#        default_status = HttpCode.OK
#        try:
#            status_code = response.status_code
#        except:
#            status_code = response.status_code

    @staticmethod
    def parse_generic_old(response, ct_accept: str) -> str:
        # Check first for failure (exceptions)
        result, status = OSMResponseParsing.parse_failed(response)
#        # Check for success
#        result = parse_successful
        status = response.status_code
        print("parse_generic")
        print("  status_code={}".format(status))
        print("  response={}".format(response.__dict__))
        if status is None:
            status = HttpCode.INTERNAL_ERROR.value
#        if isinstance(result, dict):
#            result = result.get("output", result)
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
        print("----------------------")
        print(ret_data)
        print("----------------------")
        return ret_data

    @staticmethod
    def parse(response, ct_accept: str) -> str:
        print("----------------------")
        print("ct_accept={}".format(ct_accept))
        try:
            print("parse_generic 1a -> response = {}".format(response.__dict__))
        except:
            print("parse_generic 1b -> response = {}".format(response))
        default_status = HttpCode.OK
        status = default_status
        result = {}
        try:
            print(type(response._content))
            print(response.__dict__)
            print(response._content)
        except:
            pass
        response_ct = response
        # Case of response objects
        if isinstance(response, RequestsResponse):
            response_ct = response._content
            status = response.status_code
            print("\n\n\n\n\n.\n.\n.\n.RESPONSE OBJECT={},status={}".format(response_ct, status))
            # Case of dictionaries encoded in binary or text form
            try:
                if isinstance(response_ct, bytes):
                    response_ct = response_ct.decode("ascii")
                response_ct = json.loads(response_ct)
            except:
                pass
        print("status={}".format(status))
        print("999")
        print(type(response_ct))
        if ct_accept is None:
            ct_accept = AllowedContentTypes.CONTENT_TYPE_JSON.value
        try:
            if isinstance(response_ct, dict) and "error" in response_ct.keys():
                # Check first for failure (exceptions)
                parsed_f, status = OSMResponseParsing.parse_failed(response)
                print("_______________________________________")
                print(parsed_f)
                #status = parsed_f.get("status")
                print("status={}".format(status))
                print("111")
                print(result)
                print("222")
                result.update({"error": parsed_f.get("error")})
                print(result)
            else:
                # Otherwise provide anything as it is
                #result.update(
                #    OSMResponseParsing.parse_normal(response, ct_accept))
                print("333 normal parsing")
                result = OSMResponseParsing.parse_normal(response, ct_accept)
        except Exception as e:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> EXCEPTION={}".format(e))
            status = HttpCode.INTERNAL_ERROR
            try:
                e_msg = e.msg
            except Exception:
                e_msg = e.__str__()
            result.update({
                "error": str(e_msg)
            })
        print("parse_generic -> result = {}".format(result))
        print("----------------------")
        # return result
        # del(result["status"])
        if status is None:
            status = default_status
        return (result, status)
#        return HttpResponse.infer(result, status, ct_accept)

    # NB: this is the correct file to keep
    @staticmethod
    def parse_send(response, ct_accept: str) -> str:
        result, status = OSMResponseParsing.parse(response, ct_accept)
        return HttpResponse.infer(result, status, ct_accept)
