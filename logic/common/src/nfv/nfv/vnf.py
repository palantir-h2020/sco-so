#!/usr/bin/env python3
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


class VnsfoVnsf:

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

    # Packages

    def get_vnfr_config(self, vnf_name=None):
        return self.orchestrator.get_vnf_descriptors(vnf_name)

    def onboard_package(self, vnf_pkg_file):
        return self.orchestrator.upload_vnfd_package(vnf_pkg_file)
        # return self.orchestrator.onboard_package(vnf_pkg_file)

    def delete_package(self, vnf_name=None):
        return self.orchestrator.delete_package(vnf_name)

    # Running instances

    def get_vnfr_running(self, instance_id=None):
        return self.orchestrator.get_vnf_instances(instance_id)

    def exec_action_on_vnf(self, payload: Dict):
        return self.orchestrator.exec_action_on_vnf(payload)

    def submit_action_request(self,
                              vnfr_id: str = None, action: str = None,
                              params: List = list()):
        payload = {"vnfr-id": vnfr_id,
                   "action": action,
                   "params": params}
        return self.exec_action_on_vnf(payload)
