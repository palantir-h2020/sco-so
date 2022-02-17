# -*- coding: utf-8 -*-

# Copyright 2017-present i2CAT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from common.exception.exception import SOException
from common.nfv.nfvo.osm.osm_r10 import OSMR10
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from typing import Dict, List
import requests


class OSMInterfaceXNF:

    def __init__(self, release=None):
        try:
            self.orchestrator = globals().get("OSMR{}".format(release), None)
            if callable(self.orchestrator):
                self.orchestrator = self.orchestrator()
            else:
                self.orchestrator = OSMR10()
        except Exception:
            raise SOException(
                "Cannot create instance of OSMR{}".format(release))
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _select_args(self, args_list: list) -> str:
        if not isinstance(args_list, list):
            return args_list
        args_sel = list(filter(lambda x: x is not None, args_list))
        # The most prioritary argument should be in first position
        if len(args_sel) > 0:
            args_sel = args_sel[0]
        return args_sel

    # Packages

    def get_xnfr_config(self, pkg_id=None, pkg_name=None):
        filter_arg = self._select_args([pkg_id, pkg_name])
        return self.orchestrator.get_xnf_descriptors(filter_arg)

    def onboard_package(self, pkg_file):
        return self.orchestrator.upload_xnfd_package(pkg_file)

    def delete_package(self, pkg_name=None):
        return self.orchestrator.delete_package(pkg_name)

    # Running instances

    def get_xnfr_running(self, instance_id=None):
        return self.orchestrator.get_xnf_instances(instance_id)

    def exec_action_on_xnf(self, payload: Dict):
        return self.orchestrator.exec_action_on_xnf(payload)

    def submit_action_request(self,
                              id: str = None, action: str = None,
                              params: List = list()):
        payload = {"xnfr-id": id,
                   "action": action,
                   "params": params}
        print("OSMInterfaceXNF - payload={}".format(payload))
        return self.exec_action_on_xnf(payload)
