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

from common.config.parser.fullparser import FullConfParser
# from common.core import download
from common.exception.exception import SOException
from common.log.log import setup_custom_logger
# from common.db.manager import DBManager
from common.nfv.nfvo.osm.exception import OSMException, OSMPackageConflict,\
    OSMPackageError, OSMPackageNotFound, OSMUnknownPackageType,\
    OSMVNFKeyNotFound, OSMInstanceNotFound
from flask import current_app
from io import BytesIO
from mimetypes import MimeTypes
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from werkzeug.datastructures import FileStorage
# import hashlib
import json
import os
# import pycurl
import requests
import shutil
import tarfile
import threading
import time
import urllib3
import yaml


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOGGER = setup_custom_logger(__name__)
CONFIG_PATH = "../"


def check_authorization(f):
    """
    Decorator to validate authorization prior API call.
    """
    def wrapper(*args):
        response = requests.get(args[0].ns_descriptors_url,
                                headers=args[0].headers,
                                verify=False)
        if response.status_code in (401, 500):
            args[0].new_token(args[0].username,
                              args[0].password)
        return f(*args)
    return wrapper


class OSM():
    """
    OSM northbound API client (NBI).
    """

    def __init__(self):
        self.config = FullConfParser()
        self.nfvo_category = self.config.get("nfvo.yaml")
        self._read_cfg_osm_nbi(self.nfvo_category.get("osm"))
        self._create_ep_osm()
        self._create_session()
        # FIXME validate which is the best value, add to cfg
        self.monitoring_interval = 1
        self.monitoring_timeout = 60
        self._read_cfg_vnfs(self.nfvo_category.get("vnfs"))

    def _read_cfg_osm_nbi(self, cfg_section: str):
        cfg_osm_nbi = cfg_section.get("nbi")
        self.base_url = "{0}://{1}:{2}".format(
            cfg_osm_nbi.get("protocol"),
            cfg_osm_nbi.get("host"),
            cfg_osm_nbi.get("port"))
        self.username = cfg_osm_nbi.get("username")
        self.password = cfg_osm_nbi.get("password")

    def _read_cfg_vnfs(self, cfg_section: str):
        cfg_vnfs_gen = cfg_section.get("general")
        self.vnf_user = cfg_vnfs_gen.get("user")
        try:
            curr_path = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(curr_path, "../../../../../../data/key")
            with open("{}/{}".format(
                  key_path, cfg_vnfs_gen.get("key"))) as fhandle:
                self.vnf_key = fhandle.read()
        except Exception as e:
            raise OSMVNFKeyNotFound(e)

    def _create_ep_osm(self):
        self.token_url = "{0}/osm/admin/v1/tokens".format(self.base_url)
        self.ns_descriptors_url = "{0}/osm/nsd/v1/ns_descriptors".\
                                  format(self.base_url)
        self.ns_descriptors_content_url = \
            "{0}/osm/nsd/v1/ns_descriptors_content".\
            format(self.base_url)
        self.vnf_descriptors_url = "{0}/osm/vnfpkgm/v1/vnf_packages".\
                                   format(self.base_url)
        self.vnf_instances_url = "{0}/osm/nslcm/v1/vnfrs".\
                                 format(self.base_url)
        self.instantiation_url = "{0}/osm/nslcm/v1/ns_instances".\
                                 format(self.base_url)
        self.vim_accounts_url = "{0}/osm/admin/v1/vim_accounts".\
                                format(self.base_url)
        self.exec_action_url = \
            "{0}/osm/nslcm/v1/ns_instances/<ns_instance_id>/action".\
            format(self.base_url)
        self.vnfd_package_url = "{0}/osm/vnfpkgm/v1/vnf_packages_content".\
                                format(self.base_url)
        self.nsd_package_url = "{0}/osm/nsd/v1/ns_descriptors_content".\
                               format(self.base_url)

    def _create_session(self):
        self.headers = {"Accept": "application/json"}
        self.token = None

    def new_token(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        response = requests.post(self.token_url,
                                 json={"username": self.username,
                                       "password": self.password},
                                 headers=self.headers,
                                 verify=False)
        token = json.loads(response.text).get("id")
        self.headers.update({"Authorization": "Bearer {0}".format(token)})
        return token

    @check_authorization
    def get_ns_descriptor_id(self, ns_name):
        response = requests.get(self.ns_descriptors_url,
                                headers=self.headers,
                                verify=False)
        nsds = json.loads(response.text)
        for nsd in nsds:
            # (id == name) != _id
            if nsd["id"] == ns_name:
                return nsd["_id"]
        return

    @check_authorization
    def get_vnf_descriptor_id(self, vnf_name):
        response = requests.get(self.vnf_descriptors_url,
                                headers=self.headers,
                                verify=False)
        vnfds = json.loads(response.text)
        for vnfd in vnfds:
            if vnfd.get("name", None) == vnf_name:
                return vnfd["_id"]
        return

    @check_authorization
    def get_ns_descriptors(self, ns_name=None):
        response = requests.get(self.ns_descriptors_url,
                                headers=self.headers,
                                verify=False)
        nsds = json.loads(response.text)
        if ns_name:
            return {"ns": [
                self.filter_output_nsd(x) for x in nsds
                if x["name"] == ns_name]
                }
        return {"ns": [self.filter_output_nsd(x) for x in nsds]}

    @check_authorization
    def get_vnf_descriptors(self, vnf_name=None):
        response = requests.get(self.vnf_descriptors_url,
                                headers=self.headers,
                                verify=False)
        vnfs = json.loads(response.text)
        if vnf_name:
            return {"vnf": [
                self.filter_output_vnfd(x) for x in vnfs
                if x["name"] == vnf_name]
                }
        return {"vnf": [self.filter_output_vnfd(x) for x in vnfs]}

    def filter_output_nsd(self, nsd):
        out_nsd = {}
        out_nsd["name"] = nsd["id"]
        out_nsd["id"] = nsd["_id"]
        out_nsd["description"] = nsd["description"]
        out_nsd["vendor"] = nsd.get("vendor", None)
        out_nsd["version"] = nsd.get("version", None)
        out_nsd["vnfs"] = nsd["vnfd-id"]
        out_nsd["virtual-links"] = [
            x["id"] for x in nsd.get("virtual-link-desc", [])
            ]
        return out_nsd

    def filter_output_vnfd(self, vnf):
        out_vnfd = {}
        out_vnfd["name"] = vnf["id"]
        out_vnfd["id"] = vnf["_id"]
        out_vnfd["description"] = vnf["description"]
        out_vnfd["vendor"] = vnf.get("vendor", None)
        out_vnfd["version"] = vnf.get("version", None)
        try:
            vnf_lcm_ops_cfg = vnf["df"][0]["lcm-operations-configuration"]
            vnf_lcm_vnf_ops_cfg = vnf_lcm_ops_cfg["operate-vnf-op-config"]
            vnf_lcm_vnf_ops_day12_cfg = vnf_lcm_vnf_ops_cfg["day1-2"]
            day0_prims = [
                x["name"] for x in
                vnf_lcm_vnf_ops_day12_cfg[0]["initial-config-primitive"]
                ]
            day12_prims = []
            for day12_prim in vnf_lcm_vnf_ops_day12_cfg:
                config_prim = day12_prim["config-primitive"][0]
                day12_prims.append(config_prim["name"])
            out_vnfd["config-actions"] = {
                "day0": day0_prims, "day1-2": day12_prims
                }
        except Exception:
            out_vnfd["config-actions"] = []
        try:
            vnf_inst_level = vnf["df"][0]["instantiation-level"]
            vnf_vdu_struct = vnf_inst_level[0]["vdu-level"][0]
            out_vnfd["vdus"] = vnf_vdu_struct["number-of-instances"]
        except Exception:
            out_vnfd["vdus"] = 0
        nss = self.get_ns_descriptors()
        for ns in nss["ns"]:
            for cvnf in ns.get("constituent-vnfs", []):
                if cvnf["vnfd-id-ref"] == vnf["name"]:
                    out_vnfd["ns-name"] = ns["ns-name"]
        return out_vnfd

    @check_authorization
    def get_ns_descriptors_content(self):
        response = requests.get(self.ns_descriptors_content_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    @check_authorization
    def get_pnf_descriptors(self):
        response = requests.get(self.pnf_descriptors_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    def apply_mspl_action(self, instance_id, inst_md):
        if ("action" not in inst_md) or ("params" not in inst_md):
            return
        target_status = None
        # FIXME
        target_status = "running"
        if "target_status" in inst_md:
            target_status = inst_md["target_status"]
        # Passing also current_app._get_current_object() (flask global context)
        # # FIXME adapt to FastAPI
        print("[DEBUG] Launching thread to monitor status")
        t = threading.Thread(target=self.deployment_monitor_thread,
                             args=(instance_id,
                                   inst_md["action"],
                                   inst_md["params"],
                                   current_app._get_current_object(),
                                   target_status))
        t.start()

    def deployment_monitor_thread(self, instance_id, action,
                                  params, app, target_status=None):
        timeout = self.monitoring_timeout
        action_submitted = False
        # FIXME
        target_status = "running"
        # if target_status is None:
        #     target_status = self.monitoring_target_status
        while not action_submitted:
            time.sleep(self.monitoring_interval)
            timeout = timeout-self.monitoring_interval
            # print("Checking {0} {1} {2}".format(instance_id, action, params))
            try:
                nss = self.get_ns_instances(instance_id)
                LOGGER.debug("Monitored list of NSs={}".format(nss))
            except OSMException:
                LOGGER.info("No instance found, aborting configuration")
                break
            if timeout < 0:
                LOGGER.info("Timeout reached, aborting thread")
                break
            if not nss:
                LOGGER.info("No instance found, aborting thread")
                break
            operational_status = nss.get("operational-status", "")
            LOGGER.debug("operational_status = {}".format(operational_status))
            if operational_status == "failed":
                LOGGER.info("Instance failed, aborting")
                break
            if operational_status == target_status and \
               "constituent-vnfr-ref" in nss:
                # Perform action on all vnf instances?
                for vnf_instance in nss["constituent-vnfr-ref"]:
                    # exec_tmpl = self.fill_vnf_action_request_encoded(
                    #     vnf_instance["vnfr_id"], action, params)
                    payload = {"action": action,
                               "params": params}
                    output = self.exec_action_on_vnf(payload, instance_id)
                    output = "{}"
                    if action is not None:
                        app.mongo.store_vnf_action(vnf_instance,
                                                   action,
                                                   params,
                                                   json.loads(output))
                        LOGGER.info(
                            "Action performed and stored, exiting thread")
                        LOGGER.info(output)
                    action_submitted = True
            else:
                LOGGER.debug("Operational status: {0}, waiting ...".
                             format(operational_status))
        return

    @check_authorization
    def post_ns_instance(self, inst_md):
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
        vim_id = inst_md.get("vim-id")
        nsd_id = inst_md.get("ns-id", None)
        if not nsd_id:
            nsd_id = self.get_ns_descriptor_id(inst_md["ns-name"])
        LOGGER.info("VIM ID = {0}".format(vim_id))
        ns_data = {"nsdId": nsd_id,
                   "nsName": inst_md["instance-name"],
                   "nsDescription": "Instance of pkg={}".format(
                       inst_md["ns-name"]),
                   "vimAccountId": vim_id}

        # FIXME
        self.instantiation_url = "{0}/osm/nslcm/v1/ns_instances_content".\
                                 format(self.base_url)
        response = requests.post(self.instantiation_url,
                                 headers=self.headers,
                                 verify=False,
                                 json=ns_data)
        response_data = json.loads(response.text)
        resp = response

        # response = requests.post(self.instantiation_url,
        #                          headers=self.headers,
        #                          verify=False,
        #                          json=ns_data)
        # response_data = json.loads(response.text)
        # resp = response
        # inst_url = "{0}/{1}/instantiate".format(self.instantiation_url,
        #                                         response_data["id"])
        # resp = requests.post(inst_url,
        #                      headers=self.headers,
        #                      verify=False,
        #                      json=ns_data)
        # FIXME return proper data (ns-id, for instance)
        if resp.status_code in (200, 201, 202):
            success_msg = {"instance-name": inst_md["instance-name"],
                           "instance-id": response_data["id"],
                           "ns-name": inst_md["ns-name"],
                           "vim-id": vim_id,
                           "result": "success"}
            self.apply_mspl_action(response_data["id"], inst_md)
            return success_msg
        else:
            error_msg = {"result": "error",
                         "error-response": resp}
            return error_msg

    @check_authorization
    def delete_ns_instance(self, nsr_id):
        inst_url = "{0}/{1}".format(self.instantiation_url,
                                    nsr_id)
        response = requests.post(
            "{0}/terminate".format(inst_url),
            headers=self.headers,
            verify=False)
        if not str(response.status_code).startswith("2"):
            SOException.conflict_from_client(
                "NS instance with id={} does not exist".format(nsr_id))
        requests.delete("{0}".format(inst_url),
                        headers=self.headers,
                        verify=False)
        # Uncomment next lines for asynchronous behaviour
        # t = threading.Thread(target=self.monitor_ns_deletion,
        #                      args=(nsr_id,
        #                            current_app._get_current_object()))
        # t.start()
        # Comment next line for asynchronous behaviour
        self.monitor_ns_deletion(nsr_id, current_app._get_current_object())
        success_msg = {"instance-id": nsr_id,
                       "action": "delete",
                       "result": "success"}
        return success_msg

    @check_authorization
    def monitor_ns_deletion(self, ns_instance_id, app):
        timeout = self.monitoring_timeout
        inst_url = "{0}/{1}".format(self.instantiation_url,
                                    ns_instance_id)
        while timeout > 0:
            try:
                ns_status = self.get_ns_instances(ns_instance_id)
                status = ns_status["ns"][0]["operational-status"].lower()
                LOGGER.info("Operational Status = {0}".format(status))
                if status == "terminated":
                    LOGGER.info("Terminated already")
                    break
            except OSMException:
                break
            timeout -= 1
            time.sleep(1)
        delete = requests.delete(inst_url,
                                 headers=self.headers,
                                 verify=False)
        LOGGER.info("Terminating {0}".format(delete.text))

    @check_authorization
    def get_ns_instance_name(self, nsr_id):
        inst_url = "{0}/{1}".format(self.instantiation_url,
                                    nsr_id)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        ns_instances = json.loads(response.text)
        iparams = ns_instances.get("instantiate-params", None)
        if iparams:
            return iparams.get("nsName", None)
        else:
            return None

    @check_authorization
    def get_ns_instances(self, nsr_id=None):
        if nsr_id is not None:
            inst_url = "{0}/{1}".format(self.instantiation_url,
                                        nsr_id)
        else:
            inst_url = "{0}".format(self.instantiation_url)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        ns_instances = json.loads(response.text)
        if nsr_id is not None:
            return {"ns": [self.filter_output_nsi(ns_instances)]}
        ns_data = {"ns":
                   [self.filter_output_nsi(x) for x in ns_instances]}
        return ns_data

    def filter_output_nsi(self, nsi):
        out_nsi = {}
        out_nsi["config-status"] = nsi.get("config-status", "null")
        out_nsi["constituent-vnf-instances"] = []
        if "_id" not in nsi:
            raise OSMInstanceNotFound("NS instance was not found")
        vnfis = self.get_vnf_instances(nsi["_id"])
        for vnfi in vnfis:
            vnfi.update({"ns-name": nsi.get("ns-name", nsi.get("name"))})
            vnfi.update({"vnfr-name": "{0}__{1}__1".format(nsi["nsd-name-ref"],
                                                           vnfi["vnfd-id"])})
            # FIXME
            # Reminder: populate existing config jobs from the model
            # dbm = DBManager()
            # vnfi.update({"config-jobs":
            #              dbm.get_vnf_actions(vnfi["vnfr-id"])})
            out_nsi["constituent-vnf-instances"].append(vnfi)
        out_nsi["instance-id"] = nsi["id"]
        out_nsi["instance-name"] = nsi["name"]
        # out_nsi["name"] = nsi["name"]
        out_nsi["ns-name"] = nsi["nsd-name-ref"]
        out_nsi["nsd-id"] = nsi["nsd-ref"]
        out_nsi["operational-status"] = nsi["operational-status"]
        if out_nsi["operational-status"] == "ACTIVE":
            out_nsi["operational-status"] = "running"
        out_nsi["vlrs"] = vnfis[0].get("vlrs", [])
        return out_nsi

    @check_authorization
    def get_vnf_instances(self, ns_instance_id=None):
        if ns_instance_id is None:
            nss = self.get_ns_instances()
            nss_ids = [x["instance-id"] for x in nss["ns"]]
            vnfs = []
            for ns_instance_id in nss_ids:
                url = "{0}?nsr-id-ref={1}".format(
                    self.vnf_instances_url, ns_instance_id)
                response = requests.get(url,
                                        headers=self.headers,
                                        verify=False)
                for vnf in json.loads(response.text):
                    vnfs.append(vnf)
            return {"vnf":
                    [self.filter_output_vnfi(x)
                     for x in vnfs]}
        url = "{0}?nsr-id-ref={1}".format(
            self.vnf_instances_url, ns_instance_id)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vnfis = json.loads(response.text)
        return [self.filter_output_vnfi(x) for x in vnfis]

    @check_authorization
    def filter_output_vnfi(self, vnfi):
        out_vnfi = {}
        vdur = {}
        if len(vnfi["vdur"]) > 0:
            vdur = vnfi["vdur"][0]
        out_vnfi["operational-status"] = vdur.get("status", "null")
        if out_vnfi["operational-status"] == "ACTIVE":
            out_vnfi["operational-status"] = "running"
        out_vnfi["config-status"] = "config-not-needed"
        out_vnfi["ip"] = vdur.get("ip-address", "null")
        out_vnfi["ns_id"] = vnfi.get("nsr-id-ref")
        vnfd = self.get_vnf_descriptor(vnfi.get("vnfd-ref", "null"))
        if vnfd:
            out_vnfi["vendor"] = vnfd["vendor"]
        else:
            out_vnfi["vendor"] = None
        vim = self.get_vim_account(vnfi.get("vim-account-id"))
        if vim:
            out_vnfi["vim"] = vim["name"]
        else:
            out_vnfi["vim"] = None
        out_vnfi["vnfd-id"] = vnfi["vnfd-ref"]
        out_vnfi["vnfr-name"] = vnfi["vnfd-ref"]
        out_vnfi["vnfr-id"] = vnfi["id"]
        # Note: OSM returns inconsistent naming for keys in this example
        out_vnfi["ns-name"] = self.get_ns_instance_name(out_vnfi["ns_id"])
        return out_vnfi

    @check_authorization
    def get_vnf_descriptor(self, vnf_name):
        url = "{0}?name={1}".format(
            self.vnf_descriptors_url, vnf_name)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vnfds = json.loads(response.text)
        target_vnfd = None
        for vnfd in vnfds:
            if vnfd["name"] == vnf_name:
                target_vnfd = vnfd
        return target_vnfd

    @check_authorization
    def get_vim_account(self, vim_account_id):
        url = "{0}".format(self.vim_accounts_url)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vims = json.loads(response.text)
        target_vim = None
        for vim in vims:
            if str(vim["_id"]) == str(vim_account_id):
                target_vim = vim
        return target_vim

    def get_instance_id_by_vnfr_id(self, instances, vnfr_id):
        LOGGER.info("Getting instance_id by vnf_id")
        LOGGER.info("VNFR_ID {0}".format(vnfr_id))
        for instance in instances:
            for vnf_instance in instance.get(
                    "constituent-vnf-instances", []):
                if vnf_instance["vnfr-id"] == vnfr_id:
                    return instance["instance-id"]

    @check_authorization
    def exec_action_on_vnf(self, payload, instance_id=None):
        # JSON
        # resp = requests.post(
        #        endpoints.VNF_ACTION_EXEC,
        #        headers=endpoints.post_default_headers(),
        #        data=json.dumps(payload),
        #        verify=False)

        # Encoded
        # payload = payload.replace('\\"', '"').strip()
        # Find out which ns_id holds the vnf:
        if instance_id is None:
            LOGGER.info("Instance id is none")
            instance_id = self.get_instance_id_by_vnfr_id(
                self.get_ns_instances()["ns"],
                payload["vnfr-id"])
            if not instance_id:
                raise OSMException
        nsi = self.get_ns_instances(instance_id)["ns"][0]
        nsi_id = nsi["instance-id"]
        url = self.exec_action_url
        instance_url = url.replace("<ns-instance-id>", nsi_id)
        LOGGER.info(nsi_id)
        # FIXME in case the call does not work,
        # use underscore instead of hyphen
        osm_payload = {
            "member-vnf-index": "1",
            "primitive": payload["action"],
            "primitive-params": payload["params"]}
        resp = requests.post(
            instance_url,
            headers=self.headers,
            data=yaml.dump(osm_payload),
            verify=False)
        LOGGER.info("POST TO URL: ==================·····")
        LOGGER.info(instance_url)
        LOGGER.info("HEADERS: ======================·····")
        LOGGER.info(self.headers)
        LOGGER.info("WITH PAYLOAD: =================·····")
        LOGGER.info(osm_payload)
        LOGGER.info("RESPONSE TEXT: ================·····")
        LOGGER.info(resp.text)
        LOGGER.info("RESPONSE STATUS CODE: =========·····")
        LOGGER.info(resp.status_code)
        LOGGER.info("===============================·····")
        output = resp.text
        return output

    def submit_action_request(self, vnfr_id=None, action=None, params=list()):
        params_exist = all(map(lambda x: x is not None,
                               [vnfr_id, action, params]))
        if not params_exist:
            return {"Error": "Missing argument"}
        exec_tmpl = self.fill_vnf_action_request_encoded(
            vnfr_id, action, params)
        output = self.exec_action_on_vnf(exec_tmpl)
        try:
            output_dict = json.loads(output)
        except Exception:
            return {"Error": "SO-ub output is not valid JSON",
                    "output": output}
        # Keep track of remote action per vNSF
        if action is not None:
            current_app.mongo.store_vnf_action(vnfr_id,
                                               action,
                                               params,
                                               output_dict)
        return output

    @check_authorization
    def post_package(self, bin_file, url):
        pass
#        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#        headers = self.headers
#        headers.update({"Content-Type": "application/gzip"})
#        hash_md5 = hashlib.md5()
#        for chunk in iter(lambda: bin_file.read(4096), b""):
#            hash_md5.update(chunk)
#        md5sum = hash_md5.hexdigest()
#        bin_file.seek(0)
#        full_file = bin_file.read()
#        bin_file.seek(0)
#        headers.update({"Content-File-MD5": md5sum})
#        headers.update({"Content-Length": str(len(full_file))})
#        headers.update({"Expect": "100-continue"})
#        curl_cmd = pycurl.Curl()
#        curl_cmd.setopt(pycurl.URL, url)
#        curl_cmd.setopt(pycurl.SSL_VERIFYPEER, 0)
#        curl_cmd.setopt(pycurl.SSL_VERIFYHOST, 0)
#        curl_cmd.setopt(pycurl.POST, 1)
#        pycurl_headers = ["{0}: {1}".format(k, headers[k]) for
#                          k in headers.keys()]
#        curl_cmd.setopt(pycurl.HTTPHEADER, pycurl_headers)
#        data = BytesIO()
#        curl_cmd.setopt(pycurl.WRITEFUNCTION, data.write)
#        postdata = bin_file.read()
#        curl_cmd.setopt(pycurl.POSTFIELDS, postdata)
#        curl_cmd.perform()
#        http_code = curl_cmd.getinfo(pycurl.HTTP_CODE)
#        if http_code == 500:
#            raise OSMPackageError
#        output = json.loads(data.getvalue().decode())
#        if http_code == 409:
#            raise OSMPackageConflict
#        return {"package": bin_file.filename,
#                "transaction_id": output["id"]}

    def post_vnfd_package(self, bin_file):
        return self.post_package(bin_file, self.vnfd_package_url)

    def post_nsd_package(self, bin_file):
        return self.post_package(bin_file, self.nsd_package_url)

    def guess_package_type(self, bin_file):
        full_file = bin_file.read()
        bin_file.seek(0)
        tar = tarfile.open(fileobj=BytesIO(full_file), mode="r:gz")
        for name in tar.getnames():
            if os.path.splitext(name)[-1] == ".yaml":
                member_file = tar.extractfile(tar.getmember(name))
                descriptor = yaml.load(member_file.read())
                if any(map(lambda x: "nsd-catalog"
                           in x, [key for key in descriptor])):
                    return "nsd"
                if any(map(lambda x: "vnfd-catalog"
                           in x, [key for key in descriptor])):
                    return "vnfd"
        return "unknown"

    def onboard_package_remote(self, pkg_path):
        pass
#        if not os.path.isfile(pkg_path):
#            try:
#                pkg_path = download.fetch_content(pkg_path)
#            except download.DownloadException:
#                raise OSMPackageNotFound
#        return self.onboard_package(pkg_path)

    def onboard_package(self, pkg_path):
        remove_after = False
        fp = None
        bin_file = None
        output = None
        if type(pkg_path) == FileStorage:
            bin_file = pkg_path
        else:
            if not os.path.isfile(pkg_path):
                remove_after = True
            if os.path.isfile(pkg_path):
                fp = open(pkg_path, "rb")
                filename = os.path.basename(pkg_path)
                mime = MimeTypes()
                content_type = mime.guess_type(pkg_path)
                bin_file = FileStorage(fp, filename, "package", content_type)
        if bin_file is not None:
            ptype = self.guess_package_type(bin_file)
            if ptype == "vnfd":
                output = self.post_vnfd_package(bin_file)
            elif ptype == "nsd":
                output = self.post_nsd_package(bin_file)
            else:
                raise OSMUnknownPackageType
        if fp is not None:
            fp.close()
        if remove_after:
            pkg_dir = os.path.dirname(pkg_path)
            shutil.rmtree(pkg_dir)
        return output

    def remove_package(self, package_name):
        descriptor_id = self.get_vnf_descriptor_id(package_name)
        descriptor_type = "vnf"
        if not descriptor_id:
            descriptor_id = self.get_ns_descriptor_id(package_name)
            descriptor_type = "ns"
        if descriptor_id is None:
            raise OSMPackageNotFound
        if descriptor_type == "ns":
            del_url = "{0}/{1}".format(
                self.ns_descriptors_url,
                descriptor_id)
        elif descriptor_type == "vnf":
            del_url = "{0}/{1}".format(
                self.vnf_descriptors_url,
                descriptor_id)
        else:
            raise OSMUnknownPackageType
        response = requests.delete("{0}".format(del_url),
                                   headers=self.headers,
                                   verify=False)
        if response.status_code in (200, 201, 202, 204):
            return {"package": package_name}
        elif response.status_code == 409:
            raise OSMPackageConflict
        else:
            raise OSMException
