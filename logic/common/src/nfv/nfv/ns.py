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

# from common.db.models.infra.node import Node as NodeModel
from common.log.log import setup_custom_logger
from common.nfv.nfvo.osm.osm_r10 import OSMR10
from common.schemas.lcm_ns import NSInstanceActionExecWaitForData

LOGGER = setup_custom_logger(__name__)


class OSMInterfaceNS:

    def __init__(self, release=None):
        try:
            if release is not None:
                self.orchestrator = globals().get("OSMR{}".format(release),
                                                  None)
                if callable(self.orchestrator):
                    self.orchestrator = self.orchestrator()
            else:
                self.orchestrator = OSMR10()
        except Exception as e:
            raise Exception(
                "{}{}. {}. Details: {}"
                .format("Cannot create instance of OSMR",
                        release,
                        "Check the constructor",
                        e))

    def _select_args(self, args_list: list) -> str:
        if not isinstance(args_list, list):
            return args_list
        args_sel = list(filter(lambda x: x is not None, args_list))
        # The most prioritary argument should be in first position
        if isinstance(args_sel, list) and len(args_sel) > 0:
            args_sel = args_sel[0]
        return args_sel

    # Packages

    def get_nsr_config(self, pkg_id=None, pkg_name=None):
        filter_arg = self._select_args([pkg_id, pkg_name])
        return self.orchestrator.get_ns_descriptors(filter_arg)

    def onboard_package(self, pkg_file):
        return self.orchestrator.upload_nsd_package(pkg_file)

    def delete_package(self, pkg_name=None):
        return self.orchestrator.delete_package(pkg_name)

    # Running instances

    def get_nsr_running(self, instance_id=None):
        return self.orchestrator.get_ns_instances(instance_id)

    def instantiate_ns(self, inst_md):
        return self.orchestrator.create_ns_instance(inst_md)

    def delete_ns(self, nsi_id, force=False):
        # TODO: recover this information in the orchestrator's DB
        # nodes = NodeModel.objects(instance_id=nsi_id)
        # for node in nodes:
        #     LOGGER.info(node.host_name)
        #     node.delete()
        return self.orchestrator.delete_ns_instance(nsi_id, force)

    def fetch_actions_in_ns(self, nsi_id, action_id=None):
        return self.orchestrator.fetch_actions_data(nsi_id, action_id)

    def apply_action(self, nsi_id, params_actions, wait_for=None):
        return self.orchestrator.apply_action(nsi_id, params_actions, wait_for)

    def fetch_healthcheck_for_ns(self, nsi_id):
        params_actions = {
            "ns-action-name": "health-check",
            "ns-action-params": {},
        }
        # Request synchronous action so to wait for it
        output = self.orchestrator.apply_action(
            nsi_id, params_actions,
            wait_for=NSInstanceActionExecWaitForData.action_output)
        return output
