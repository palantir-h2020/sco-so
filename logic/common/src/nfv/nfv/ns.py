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

from common.db.models.infra.node import Node as NodeModel
from common.core.exception import ScoException
from common.core.log import setup_custom_logger
from common.nfv.nfvo.osm.exception import OSMFailedInstantiation
from common.nfv.nfvo.osm.osm_r10 import OSMR10
from flask import current_app
# import threading
import time

LOGGER = setup_custom_logger(__name__)


class VnsfoNs:

    def __init__(self, release=None):
        try:
            self.orchestrator = globals().get("OSMR{}".format(release), None)
            if callable(self.orchestrator):
                self.orchestrator = self.orchestrator()
            else:
                self.orchestrator = OSMR10()
        except Exception:
            raise ScoException(
                "Cannot create instance of OSMR{}".format(release))

    def get_nsr_config(self, ns_name=None):
        return self.orchestrator.get_ns_descriptors(ns_name)

    def get_nsr_running(self, instance_id=None):
        return self.orchestrator.get_ns_instances(instance_id)

    def monitor_deployment(self, instantiation_data, app, target_status=None):
        # FIXME reduce clutter w.r.t. osm.py module!
        LOGGER.info("Monitoring deployment of instance: {0}".format(
            instantiation_data["instance-id"]))
        # FIXME
        # timeout = self.monitoring_timeout
        timeout = 60
        vdus_registered = False
        nss = None
        if target_status is None:
            target_status = self.monitoring_target_status
        while not vdus_registered:
            # FIXME
            self.monitoring_interval = 1
            time.sleep(self.monitoring_interval)
            nss = self.orchestrator.get_ns_instances(
                instantiation_data["instance-id"])
            if timeout < 0:
                LOGGER.info("Timeout reached, aborting")
                break
            if len(nss["ns"]) < 1:
                LOGGER.info("No instance found, aborting thread")
                break
            operational_status = nss["ns"][0].get("operational-status", "")
            config_status = nss["ns"][0].get("config-status", "")
            LOGGER.info("> Operational status = {}".format(operational_status))
            LOGGER.info("> Config status = {}\n".format(config_status))
            # TODO improve error handling
            if operational_status == "failed" or config_status == "failed":
                status_summary = "Operational status: {0}, config status: {1}"\
                    .format(
                        operational_status, config_status
                    )
                LOGGER.info("Instance failed, aborting")
                LOGGER.info("const-vnfs")
                LOGGER.info(nss["ns"][0]["constituent-vnf-instances"])
                for const_vnf in nss["ns"][0]["constituent-vnf-instances"]:
                    LOGGER.info("const-vnf")
                    LOGGER.info(const_vnf)
                    if const_vnf["operational-status"].lower() == "vim_error":
                        LOGGER.info("inside")
                        ScoException.internal_error(
                            "Error in the infrastructure. " +
                            "Details={}".format(status_summary))
                # ScoException.conflict_from_client(operational_status)
                ScoException.internal_error(
                    "Cannot instantiate NS. Details={}".format(status_summary))
            if operational_status == target_status and \
               "constituent-vn-instances" in nss["ns"][0].keys():
                LOGGER.info("Network Service Deployed")
                LOGGER.info("Constituent VNF Instance data")
                if len(nss["ns"]) == 0:
                    # No VDUs, returning
                    return
                for vnfr in nss["ns"][0]["constituent-vnf-instances"]:
                    vnfr_name = vnfr["vnfr-name"]
                    vdu_ip = vnfr["ip"]
                    vnfr_id = vnfr["vnfr-id"]
                if "authentication" not in instantiation_data:
                    instantiation_data["authentication"] = {
                        "vnf-user": self.orchestrator.vnf_user,
                        "vnf-key": self.orchestrator.vnf_key
                    }
                # app.mongo.store_vdu(vnfr_name, vdu_ip,
                #                     instantiation_data["isolation_policy"],
                #                     instantiation_data["termination_policy"],
                #                     instantiation_data["authentication"],
                #                     instantiation_data["analysis_type"],
                #                     instantiation_data["pcr0"],
                #                     instantiation_data["distribution"],
                #                     instantiation_data["driver"],
                #                     instantiation_data["instance_id"],
                #                     vnfr_id)
            timeout -= self.monitoring_interval
            # LOGGER.info("Obtained list of NSs={}".format(nss))

    # @content.on_mock(ns_m().post_nsr_instantiate_mock)
    def instantiate_ns(self, inst_md):
        # Async
        # return self.orchestrator.post_ns_instance(inst_md)
        # Sync
        # TODO Create proper model, then enforce with pydantic
        """
        Required structure (inst_md):
        {
            "ns-name": "<name for the NS package>",
            "instance-name": "<name for the NS instance>",
            "vim-id": "<UUID of the VIM>"
        }
        Optional structure (inst_md):
        {
            "ns-id": "<UUID of the NS package>"
        }
        """
        nsi_data = self.orchestrator.post_ns_instance(inst_md)
        try:
            # FIXME
            self.monitoring_target_status = "running"
            self.monitor_deployment(nsi_data,
                                    current_app._get_current_object(),
                                    self.monitoring_target_status)
            # Use in case of async
            # t = threading.Thread(target=self.monitor_deployment,
            #                      args=(nsi_data,
            #                            current_app._get_current_object(),
            #                            self.monitoring_target_status))
            # t.start()
        except OSMFailedInstantiation as service_instance_failure:
            nsi_data["result"] = "failure"
            nsi_data["error-response"] = {
                "msg": service_instance_failure.msg,
                "instance-id": nsi_data["instance-id"]
                }
            nsi_data["status_code"] = \
                service_instance_failure.status_code
        return nsi_data

    # @content.on_mock(ns_m().delete_nsr_mock)
    def delete_ns(self, instance_id):
        nodes = NodeModel.objects(instance_id=instance_id)
        for node in nodes:
            LOGGER.info(node.host_name)
            node.delete()
        return self.orchestrator.delete_ns_instance(instance_id)

    def fetch_config_nss(self):
        catalog = self.get_nsr_config()
        return catalog
