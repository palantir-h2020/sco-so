from common.server.http.http_code import HttpCode
from flask import Blueprint, make_response
# import json
import requests
# import urllib.request


so_api_bp = Blueprint("so_api", __name__)


class APIClient(object):
    def __init__(self):
        self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
                }

    def __func_template__(self, method_type, method_ep, **method_params):
        response = ""
        if method_type == "get":
            response = requests.get(method_ep)
        elif method_type == "post":
            response = requests.post(
                    method_ep, headers=self.headers,
                    json=method_params, verify=False)
        elif method_type == "put":
            response = requests.put(
                    method_ep, headers=self.headers,
                    json=method_params, verify=False)
        elif method_type == "delete":
            response = requests.delete(
                    method_ep, headers=self.headers,
                    verify=False)
        response_data = ""
        try:
            response_data = response.json()
        except Exception:
            try:
                response_data = response.text()
            except Exception:
                pass
        response_status = HttpCode.INTERNAL_ERROR
        try:
            response_status = response.status_code
        except Exception:
            pass
        return make_response(response_data, response_status)


# Option A
# req = urllib.request.Request("http://127.0.0.1:50101/openapi.json")
# api_spec_content = ""
# with urllib.request.urlopen(req) as response:
#     api_spec_content = response.read()
# api_spec_content = api_spec_content.decode("ascii")
# api_spec_content = json.loads(api_spec_content)
# Option B
api_spec_content = {'openapi': '3.0.2', 'info': {'title': 'SCO/SO API', 'description': 'API endpoints for SCO/SO', 'contact': {'name': 'Carolina Fernandez', 'email': 'carolina.fernandez@i2cat.net'}, 'version': '0.0.1'}, 'paths': {'/mon/infra': {'get': {'summary': 'Infra List', 'operationId': 'infra_list_mon_infra_get', 'responses': {'200': {'description': 'Successful Response', 'content': {'application/json': {'schema': {}}}}}}}, '/': {'get': {'summary': 'Root', 'operationId': 'root__get', 'responses': {'200': {'description': 'Successful Response', 'content': {'application/json': {'schema': {}}}}}}}}}

# Code to parse the received OpenAPI spec
# and create clients on-the-fly to be able
# to expose similar endpoints to the user
# (in this side, the API) and to call the
# endpoints indicated in the spec (in the
# other side, each module in SCO/SO)
ep_base = "http://127.0.0.1:50101"
for endpoint, ep_details in api_spec_content.get("paths").items():
    # print("name={}".format(endpoint))
    api_x_client = APIClient()
    for ep_method_type, ep_meth_det in ep_details.items():
        # print(" - method_type={}".format(ep_method_type))
        ep_meth_name = ep_meth_det.get("operationId")
        # print(" - method_name={}".format(ep_meth_name))
        f_x = api_x_client.__func_template__("{}{}".format(
            ep_base, ep_method_type), endpoint)
        # NB: both fail w.r.t. using requests outside the app context
        # # Option A
        setattr(api_x_client, "func_{}".format(ep_meth_name), f_x)
        # # Option B
        so_api_bp.add_url_rule(endpoint, "{}".format(ep_meth_name), f_x)
