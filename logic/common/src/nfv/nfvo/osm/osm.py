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
from common.log.log import setup_custom_logger
from common.server.http.http_code import HttpCode
from common.utils import download
from common.utils.osm_response_parsing import OSMResponseParsing
from common.utils.time_handling import TimeHandling
# from common.db.manager import DBManager
from common.nfv.nfvo.osm import exception as osm_exception
from flask import current_app
from hashlib import md5 as hash_md5
from io import BytesIO
from mimetypes import MimeTypes
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from time import sleep
from uuid import uuid4
from werkzeug.datastructures import FileStorage
from yaml import dump as yaml_dump, load as yaml_load,\
    FullLoader as yaml_full_loader
import json
import os
import pycurl
import requests
import shutil
import tarfile
import threading
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


LOGGER = setup_custom_logger(__name__)
CONFIG_PATH = "../"


def check_authorization(f):
    """
    Decorator to validate authorization prior API call.
    """
    def wrapper(*args):
        response = requests.get(args[0].url_token,
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
    See OSM endpoints in https://<osm_ip>:9999/osm/
    """

    def __init__(self):
        self.config = FullConfParser()
        self.nfvo_category = self.config.get("so.yaml")
        self.osm_section = self.nfvo_category.get("osm")
        self._read_cfg_osm(self.osm_section)
        self._create_ep_osm()
        self._create_session()
        self.mon_section = self.nfvo_category.get("monitoring")
        self._read_cfg_monitoring(self.mon_section)
        # self.monitoring_interval = 1
        # self.monitoring_timeout = 60
        self._read_cfg_vnfs(self.nfvo_category.get("nfs"))
        # Definition of expected/target status upon operations
        self.deployment_expected_status = "running"
        self.deletion_expected_status = "terminated"
        self.force_deletion_expected_status = "failed"
        # self.osm_builtin_actions = ["initiate", "scale",
        #    "terminate", "update"]
        self.osm_builtin_actions = ["instantiate", "scale", "terminate"]

    def _read_cfg_osm(self, cfg_section: dict):
        cfg_osm_nbi = cfg_section.get("nbi")
        self.base_url = "{0}://{1}:{2}".format(
            cfg_osm_nbi.get("protocol"),
            cfg_osm_nbi.get("host"),
            cfg_osm_nbi.get("port"))
        self.username = cfg_osm_nbi.get("username")
        self.password = cfg_osm_nbi.get("password")
        cfg_osm_vim = cfg_section.get("vim")
        self.vim_fallback = cfg_osm_vim.get("fallback")

    def _read_cfg_monitoring(self, cfg_section: dict):
        self.monitoring_interval = cfg_section.get("interval")
        self.monitoring_timeout = cfg_section.get("timeout")

    def _read_cfg_vnfs(self, cfg_section: dict):
        cfg_vnfs_gen = cfg_section.get("general")
        self.vnf_user = cfg_vnfs_gen.get("user")
        try:
            curr_path = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(curr_path, "../../../../keys")
            with open("{}/{}".format(
                  key_path, cfg_vnfs_gen.get("key"))) as fhandle:
                self.vnf_key = fhandle.read()
        except Exception as e:
            raise osm_exception.OSMVNFKeyNotFound(e)

    def _create_ep_osm(self):
        def _ep(url):
            # Note: initial "/" shall be provided in "url"
            return "{0}/osm{1}".format(self.base_url, url)

        # Authentication
        self.url_token = _ep("/admin/v1/tokens")
        # Package descriptors (NSD, VNFD)
        self.url_nsd_list = _ep("/nsd/v1/ns_descriptors")
        self.url_nsd_detail = _ep("/nsd/v1/ns_descriptors_content")
        self.url_vnfd_list = _ep("/vnfpkgm/v1/vnf_packages")
        self.url_vnfd_detail = _ep("/vnfpkgm/v1/vnf_packages_content")
        # Running instances (NSI, VNFI) and actions (on NSs)
        self.url_nsi_list = _ep("/nslcm/v1/ns_instances")
        self.url_nsi_detail = _ep("/nslcm/v1/ns_instances_content")
        self.url_nsd_action = _ep("/nslcm/v1/ns_instances/{}/action")
        # Actions on running instances (NSI)
        self.url_nsi_action_detail = _ep("/nslcm/v1/ns_lcm_op_occs")
        # Records of running instances (NSR, VNFR)
        self.url_vnfr_detail = _ep("/nslcm/v1/vnfrs")
        # Infrastructure
        self.url_vim_list = _ep("/admin/v1/vim_accounts")

    # Authentication

    def _create_session(self):
        self.headers = {"Accept": "application/json"}
        self.token = None

    def new_token(self, username=None, password=None):
        if username is not None:
            self.username = username
        if password is not None:
            self.password = password
        response = requests.post(self.url_token,
                                 json={"username": self.username,
                                       "password": self.password},
                                 headers=self.headers,
                                 verify=False)
        token = json.loads(response.text).get("id")
        self.headers.update({"Authorization": "Bearer {0}".format(token)})
        return token

    # Packages

    @check_authorization
    def get_ns_descriptor(self, ns_filter):
        """
        Given a name (or ID), returns the NSD.
        """
        response = requests.get(self.url_nsd_list,
                                headers=self.headers,
                                verify=False)
        nsds = json.loads(response.text)
        for nsd in nsds:
            if nsd.get("name", None) == ns_filter or\
                    nsd.get("product-name", None) == ns_filter or\
                    nsd.get("_id", None) == ns_filter:
                return nsd
        return

    @check_authorization
    def get_vnf_descriptor(self, vnf_filter):
        """
        Given a name (or ID), returns the VNFD.
        """
        response = requests.get(self.url_vnfd_list,
                                headers=self.headers,
                                verify=False)
        vnfds = json.loads(response.text)
        for vnfd in vnfds:
            if vnfd.get("name", None) == vnf_filter or\
                    vnfd.get("product-name", None) == vnf_filter or\
                    vnfd.get("_id", None) == vnf_filter:
                return vnfd
        return

    # Called externally
    @check_authorization
    def get_ns_descriptors(self, ns_filter=None):
        response = requests.get(self.url_nsd_list,
                                headers=self.headers,
                                verify=False)
        nsds = json.loads(response.text)
        result = nsds
        if ns_filter is not None and not isinstance(ns_filter, list):
            nsd = self.get_ns_descriptor(ns_filter)
            if nsd is None:
                raise osm_exception.OSMPackageError(
                    {"error": "Package {} does not exist".format(ns_filter),
                     "status": HttpCode.NOT_FOUND})
            result = nsd
        if not isinstance(result, list):
            result = [result]
        return {
            "ns": list(map(lambda x: self.filter_output_nsd(x), result)),
            "status": HttpCode.OK}

    # Called externally
    @check_authorization
    def get_vnf_descriptors(self, vnf_filter=None):
        response = requests.get(self.url_vnfd_list,
                                headers=self.headers,
                                verify=False)
        vnfs = json.loads(response.text)
        result = vnfs
        if vnf_filter is not None and not isinstance(vnf_filter, list):
            vnfd = self.get_vnf_descriptor(vnf_filter)
            if vnfd is None:
                raise osm_exception.OSMPackageError(
                    {"error": "Package {} does not exist".format(vnf_filter),
                     "status": HttpCode.NOT_FOUND})
            result = vnfd
        if not isinstance(result, list):
            result = [result]
        return {
            "vnf": list(map(lambda x: self.filter_output_vnfd(x), result)),
            "status": HttpCode.OK}

    def filter_output_nsd(self, nsd):
        out_nsd = {}
        out_nsd["name"] = nsd.get("id")
        out_nsd["id"] = nsd.get("_id")
        out_nsd["description"] = nsd.get("description")
        out_nsd["vendor"] = nsd.get("vendor", None)
        out_nsd["version"] = nsd.get("version", None)
        out_nsd["vnfs"] = nsd.get("vnfd-id")
        out_nsd["virtual-links"] = [
            x["id"] for x in nsd.get("virtual-link-desc", [])
            ]
        return out_nsd

    def filter_output_vnfd(self, vnf):
        out_vnfd = {}
        out_vnfd["name"] = vnf.get("id")
        out_vnfd["id"] = vnf.get("_id")
        out_vnfd["description"] = vnf.get("description")
        out_vnfd["vendor"] = vnf.get("vendor", None)
        out_vnfd["version"] = vnf.get("version", None)
        try:
            vnf_lcm_ops_cfg = \
                    vnf.get("df", [{}])[0]["lcm-operations-configuration"]
            vnf_lcm_vnf_ops_cfg = vnf_lcm_ops_cfg.get("operate-vnf-op-config")
            vnf_lcm_vnf_ops_day12_cfg = vnf_lcm_vnf_ops_cfg.get("day1-2")
            day0_prims = [
                x.get("name") for x in
                vnf_lcm_vnf_ops_day12_cfg[0].get("initial-config-primitive")
                ]
            day12_prims = []
            for day12_prim in vnf_lcm_vnf_ops_day12_cfg:
                config_prim = day12_prim.get("config-primitive")[0]
                day12_prims.append(config_prim.get("name"))
            out_vnfd["config-actions"] = {
                "day0": day0_prims, "day1-2": day12_prims
                }
        except Exception:
            out_vnfd["config-actions"] = []
        try:
            vnf_inst_level = vnf.get("df")[0]["instantiation-level"]
            vnf_vdu_struct = vnf_inst_level[0]["vdu-level"][0]
            out_vnfd["vdus"] = vnf_vdu_struct.get("number-of-instances")
        except Exception:
            out_vnfd["vdus"] = 0
        nss = self.get_ns_descriptors()
        for ns in nss["ns"]:
            for cvnf in ns.get("constituent-vnfs", []):
                if cvnf["vnfd-id-ref"] == vnf.get("name"):
                    out_vnfd["ns-name"] = ns.get("ns-name")
        return out_vnfd

    @check_authorization
    def get_ns_descriptors_content(self):
        response = requests.get(self.url_nsd_detail,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    @check_authorization
    def get_pnf_descriptors(self):
        response = requests.get(self.pnf_descriptors_url,
                                headers=self.headers,
                                verify=False)
        return json.loads(response.text)

    # Called externally
    @check_authorization
    def upload_package(self, bin_file, url):
        # Note that using requests produces a 401 error
        # Instead, use the Python cURL implementation
        # and set proper flags
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        headers = self.headers
        headers.update({"Content-Type": "application/gzip"})
        hash_md5_res = hash_md5()
        pkg_chunk = ""
        for chunk in iter(lambda: bin_file.read(4096), b""):
            # Copy the first part for later processing
            if len(pkg_chunk) == 0:
                pkg_chunk += str(chunk)
            hash_md5_res.update(chunk)
        # # Attempt to retrieve name for package
        # # package_name = bin_file.filename
        # try:
        #     idx_r = pkg_chunk.find(".tar")
        #     idx_l = pkg_chunk[:idx_r].rfind("\\x")
        #     # package_name = pkg_chunk[idx_l+4:idx_r]
        # except Exception as e:
        #     package_name = ""
        md5sum = hash_md5_res.hexdigest()
        bin_file.seek(0)
        full_file = bin_file.read()
        bin_file.seek(0)
        headers.update({"Content-File-MD5": md5sum})
        headers.update({"Content-Length": str(len(full_file))})
        headers.update({"Expect": "100-continue"})
        curl_cmd = pycurl.Curl()
        curl_cmd.setopt(pycurl.URL, url)
        curl_cmd.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl_cmd.setopt(pycurl.SSL_VERIFYHOST, 0)
        curl_cmd.setopt(pycurl.POST, 1)
        pycurl_headers = ["{0}: {1}".format(k, headers[k]) for
                          k in headers.keys()]
        curl_cmd.setopt(pycurl.HTTPHEADER, pycurl_headers)
        data = BytesIO()
        curl_cmd.setopt(pycurl.WRITEFUNCTION, data.write)
        postdata = bin_file.read()
        curl_cmd.setopt(pycurl.POSTFIELDS, postdata)
        curl_cmd.perform()
        http_code = curl_cmd.getinfo(pycurl.HTTP_CODE)
        output = json.loads(data.getvalue().decode())
        if http_code == 401:
            raise osm_exception.SOException(
                    {"error": "Authentication issue",
                     "status": http_code})
        if http_code == 409:
            raise osm_exception.OSMPackageConflict(
                    {"error": output.get("detail"),
                     "status": http_code})
        if http_code == 422:
            raise osm_exception.OSMPackageError(
                    {"error": output.get("detail"),
                     "status": http_code})
        if http_code >= 500:
            raise osm_exception.OSMPackageError(
                    {"error": "Internal server error",
                     "status": http_code})
        return {
            "id": output.get("id"),
            "status": HttpCode.ACCEPTED}

    def upload_vnfd_package(self, bin_file):
        # Endpoint: "/vnfpkgm/v1/vnf_packages_content"
        return self.upload_package(bin_file, self.url_vnfd_detail)

    def upload_nsd_package(self, bin_file):
        # Endpoint: "/nsd/v1/ns_descriptors_content"
        return self.upload_package(bin_file, self.url_nsd_detail)

    def guess_descriptor_type(self, package_name):
        res = {}
        descriptor_id = None
        descriptor = self.get_vnf_descriptor(package_name)
        if descriptor is not None:
            descriptor_id = descriptor.get("_id")
            res.update({"id": descriptor_id, "type": "vnf"})
        if descriptor_id is None:
            descriptor = self.get_ns_descriptor(package_name)
            if descriptor is not None:
                descriptor_id = descriptor.get("_id")
            res.update({"id": descriptor_id, "type": "ns"})
        if "id" in res.keys() and res.get("id") is None:
            res = {}
        return res

    def guess_package_type(self, bin_file):
        full_file = bin_file.read()
        bin_file.seek(0)
        tar = tarfile.open(fileobj=BytesIO(full_file), mode="r:gz")
        for name in tar.getnames():
            if os.path.splitext(name)[-1] == ".yaml":
                member_file = tar.extractfile(tar.getmember(name))
                descriptor = yaml_load(
                        member_file.read(), Loader=yaml_full_loader)
                if "nsd" in descriptor.keys():
                    return "nsd"
                if "vnfd" in descriptor.keys():
                    return "vnfd"
        return "unknown"

    def onboard_package_remote(self, pkg_path):
        # Not expected to be used
        if not os.path.isfile(pkg_path):
            try:
                pkg_path = download.fetch_content(pkg_path)
            except download.DownloadException:
                raise osm_exception.OSMPackageNotFound
        return self.onboard_package(pkg_path)

    def onboard_package(self, pkg_path):
        # Called by endpoints
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
                output = self.upload_vnfd_package(bin_file)
            elif ptype == "nsd":
                output = self.upload_nsd_package(bin_file)
            else:
                raise osm_exception.OSMUnknownPackageType
        if fp is not None:
            fp.close()
        if remove_after:
            pkg_dir = os.path.dirname(pkg_path)
            shutil.rmtree(pkg_dir)
        return output

    def delete_package(self, package_name):
        desc_data = self.guess_descriptor_type(package_name)
        descriptor_id = desc_data.get("id")
        descriptor_type = desc_data.get("type")
        if descriptor_id is None:
            raise osm_exception.OSMPackageNotFound({
                    "error": "Package {} does not exist".format(package_name),
                    "status": 409})
        if descriptor_type == "ns":
            del_url = "{0}/{1}".format(
                self.url_nsd_list,
                descriptor_id)
        elif descriptor_type == "vnf":
            del_url = "{0}/{1}".format(
                self.url_vnfd_list,
                descriptor_id)
        else:
            raise osm_exception.OSMUnknownPackageType(
                    "Package {} with unknown type".format(package_name))
        response = requests.delete("{0}".format(del_url),
                                   headers=self.headers,
                                   verify=False)
        if response.status_code >= 200 and response.status_code < 300:
            return {
                "name": package_name, "id": descriptor_id,
                "status": response.status_code}
        elif response.status_code == 409:
            parsed_error, status = OSMResponseParsing.parse_error_msg(response)
            parsed_error = parsed_error.get("detail", parsed_error)
            raise osm_exception.OSMPackageConflict(
                    {"error": parsed_error, "status": status})
        else:
            res_details = OSMResponseParsing.parse_failed(response)
            raise osm_exception.OSMException({
                    "error": str(res_details),
                    "status": HttpCode.INTERNAL_ERROR})

    # Running instances

    # Called externally
    @check_authorization
    def fetch_actions_data(self, nsi_id: str):
        actions_ret = {"ns": nsi_id, "actions": []}
        url_nsi_details = "{}/?nsInstanceId={}".format(
                              self.url_nsi_action_detail, nsi_id)
        response = requests.get(url_nsi_details,
                                headers=self.headers,
                                verify=False)
        actions_resp = response.json()
        actions_ret_list = []
        for action in actions_resp:
            action_type = action.get("lcmOperationType")
            if action_type != "action":
                action_type = "built-in ({})".format(action_type)
            action_status = action.get("operationState").lower()
            action_exec_time = TimeHandling.ms_to_rfc3339(
                    action.get("startTime"))
            action_ret = {"id": action.get("_id"),
                          "start-time": action_exec_time,
                          "type": action_type,
                          "params": action.get("operationParams"),
                          "status": action_status
                          }
            if action_status == "failed":
                action_ret.update({
                    "error": action.get("errorMessage")})
            actions_ret_list.append(action_ret)
        actions_ret.update({"actions": actions_ret_list})
        return {"status": HttpCode.OK, **actions_ret}

    def apply_action(self, nsi_id, inst_md):
        if "ns-action-name" not in inst_md.keys():
            return
        target_status = None
        if self.deployment_expected_status in inst_md:
            target_status = inst_md.get("target_status")
        # Passing also current_app._get_current_object() (flask global context)
        LOGGER.debug("[DEBUG] Launching thread to monitor status " +
                     "prior to applying action")
        t = threading.Thread(target=self.monitor_ns_deployment,
                             args=(nsi_id,
                                   inst_md.get("ns-action-name"),
                                   inst_md.get("ns-action-params"),
                                   current_app._get_current_object(),
                                   target_status))
        t.start()
        return {"status": HttpCode.ACCEPTED, "id": nsi_id, **inst_md}

    def monitor_ns_deployment(self, nsi_id, action_name, action_params,
                              app, target_status=None):
        timeout = self.monitoring_timeout
        action_submitted = False
        # A name for the action must be provided at least
        if action_name is None:
            return action_submitted
        while not action_submitted:
            sleep(self.monitoring_interval)
            timeout = timeout-self.monitoring_interval
            # print("Checking {0} {1} {2}".format(nsi_id, action, params))
            try:
                nss = self.get_ns_instances(nsi_id)
                LOGGER.debug("Monitored list of NSs={}".format(nss))
            except osm_exception.OSMException:
                LOGGER.info("No instance found, aborting configuration")
                break
            if timeout < 0:
                LOGGER.info("Timeout reached, aborting thread")
                break
            if not nss:
                LOGGER.info("No instance found, aborting thread")
                break
            # operational_status = nss.get("operational-status", "")
            operational_status = nss.get("ns")[0].get("status")\
                                    .get("operational")
            LOGGER.debug("Operational status: {0} ...".format(
                operational_status))
            if operational_status == "failed":
                LOGGER.info("Instance failed, aborting")
                break
            if operational_status == self.deployment_expected_status:
                payload = {"action": action_name,
                           "params": action_params}
                # Execute the specific action at the NS instance
                output = self.exec_action_on_ns(nsi_id, payload)
#                if action is not None:
#                    app.mongo.store_vnf_action(vnf_instance,
#                                               action,
#                                               params,
#                                               json.loads(output))
                LOGGER.info(
                    "Action performed and stored, exiting thread")
                LOGGER.info(output)
                action_submitted = True
        return action_submitted

    @check_authorization
    def create_ns_instance(self, inst_md):
        """
        Required structure (inst_md):
        {
            "ns-pkg-id": "<UUID of the NS package>",
            "vim-id": "<UUID of the VIM>"
        }
        Optional structure (inst_md):
        {
            "name": "<name for the NS instance>",
            "description": "<description for the NS instance>",
            "ssh-keys": ["key1", ..., "keyN"],
            "ns-action-name": "<name of the action to run post-creation>",
            "ns-action-params": [{"key1": "value1"}, ..., {"keyN": "valueN"}]
        }
        """
        ns_pkg_id = inst_md.get("ns-pkg-id", None)
        vim_id = inst_md.get("vim-id")
        ns_name = inst_md.get("name")
        ns_description = inst_md.get("description")
        ns_sshkeys = inst_md.get("ssh-keys")
        ns_action_name = inst_md.get("ns-action-name")
        ns_action_params = inst_md.get("ns-action-params")
        LOGGER.info("VIM ID = {0}".format(vim_id))
        nsi_data = {}
        if ns_pkg_id is not None:
            nsi_data.update({"nsdId": ns_pkg_id})
        if vim_id is None:
            vim_id = self.vim_fallback
        nsi_data.update({"vimAccountId": vim_id})
        if ns_name is None:
            ns_name = str(uuid4())
        nsi_data.update({"nsName": ns_name})
        if ns_description is not None:
            nsi_data.update({"nsDescription": ns_description})
        else:
            nsi_data.update(
                    {"nsDescription": "Instance of package with id={}".
                        format(ns_pkg_id)})
        if ns_sshkeys is not None:
            if isinstance(ns_sshkeys, str):
                ns_sshkeys = [ns_sshkeys]
            nsi_data.update({"ssh_keys": ns_sshkeys})

        response = requests.post(self.url_nsi_detail,
                                 headers=self.headers,
                                 verify=False,
                                 json=nsi_data)
        response_data = response.json()
        status_code = response_data.get("status")
        detail = response_data.get("detail")
        if status_code is None:
            status_code = HttpCode.OK
        if status_code == 400:
            if "Invalid vimAccountId" in detail:
                raise osm_exception.OSMResourceNotFound(
                    {"error": "VIM with id={} does not exist"
                      .format(ns_pkg_id)})
        elif status_code == 404:
            if "any nsd with filter" in detail:
                raise osm_exception.OSMResourceNotFound(
                    {"error": "NS package with id={} does not exist"
                        .format(ns_pkg_id)})
        elif status_code > 400:
            raise osm_exception.OSMException(
                {"error": detail, "status": status_code})

        nsr_id = response_data.get("id")

        # Asynchronous behaviour
        t = threading.Thread(target=self.monitor_ns_deployment,
                             args=(nsr_id, ns_action_name, ns_action_params,
                                   current_app._get_current_object(),
                                   self.deployment_expected_status))
        t.start()
        # Synchronous behaviour
        # self.monitor_ns_deployment(nsr_id,
        #                            ns_action_name,
        #                            ns_action_params,
        #                            current_app._get_current_object(),
        #                            self.deployment_expected_status)

        success_msg = {"id": nsr_id,
                       "status": HttpCode.ACCEPTED}
        if detail is not None:
            success_msg.update({"detail": detail})
        return success_msg

        if response_data.status_code >= 200 and\
                response_data.status_code < 400:
            success_msg = {"name": ns_name,
                           "id": response_data.get("id"),
                           "ns-pkg-id": ns_pkg_id,
                           "vim-id": vim_id,
                           "status": HttpCode.ACCEPTED}
            return success_msg
        else:
            error_msg = {"status": response_data.status.code,
                         "error": response_data}
            return error_msg

    @check_authorization
    def delete_ns_instance(self, nsr_id, force=False):
        self.exec_builtin_action_on_ns(nsr_id, "terminate")
        # Asynchronous behaviour
        t = threading.Thread(target=self.monitor_ns_deletion,
                             args=(nsr_id, force))
        t.start()
        # Synchronous behaviour
        # self.monitor_ns_deletion(nsr_id, current_app._get_current_object())
        return {"id": nsr_id, "status": HttpCode.ACCEPTED}

    @check_authorization
    def monitor_ns_deletion(self, nsi_id, force=False):
        timeout = self.monitoring_timeout
        inst_url = "{0}/{1}".format(self.url_nsi_list,
                                    nsi_id)
        while timeout > 0:
            try:
                ns_status = self.get_ns_instances(nsi_id)
                status = ns_status.get("ns")[0].get("status")\
                    .get("operational").lower()
                LOGGER.info("Monitoring status for ns={0}: {1}".format(
                    nsi_id, status))
                if status in [self.deletion_expected_status,
                              self.force_deletion_expected_status]:
                    LOGGER.info("NS with id={0} already in state={1}".format(
                        nsi_id, status))
                    break
            except Exception as e:
                LOGGER.error("Cannot retrieve status for ns={0}. Details={1}".
                             format(nsi_id, e))
                break
            timeout -= 1
            sleep(1)
        if force:
            inst_url = "{}?FORCE=true".format(inst_url)
        delete = requests.delete(inst_url,
                                 headers=self.headers,
                                 verify=False)
        LOGGER.info("Terminating {0}".format(delete.text))

    @check_authorization
    def get_ns_instance_name(self, nsr_id):
        inst_url = "{0}/{1}".format(self.url_nsi_list,
                                    nsr_id)
        response = requests.get(inst_url,
                                headers=self.headers,
                                verify=False)
        ns_instances = json.loads(response.text)
        iparams = ns_instances.get("instantiate_params", None)
        if iparams:
            return iparams.get("nsName", None)
        else:
            return None

#    # Called externally
#    @check_authorization
#    def get_ns_instances(self, nsr_id=None):
#        if nsr_id is not None:
#            inst_url = "{0}/{1}".format(self.url_nsi_list,
#                                        nsr_id)
#        else:
#            inst_url = "{0}".format(self.url_nsi_list)
#        response = requests.get(inst_url,
#                                headers=self.headers,
#                                verify=False)
#        ns_instances = json.loads(response.text)
#        if nsr_id is not None:
#            return {"ns": [self.filter_output_nsi(ns_instances)]}
#        ns_data = {"ns":
#                   [self.filter_output_nsi(x) for x in ns_instances]}
#        return ns_data

    # Called externally
    @check_authorization
    def get_ns_instances(self, nsi_id=None):
        nss = []
        if nsi_id is None:
            url = self.url_nsi_list
            response = requests.get(url,
                                    headers=self.headers,
                                    verify=False)
            nss = response.json()
        else:
            url = "{0}/{1}".format(self.url_nsi_list, nsi_id)
            response = requests.get(url,
                                    headers=self.headers,
                                    verify=False)
            result = response.json()
            if result.get("status") == 404:
                raise osm_exception.OSMInstanceNotFound(
                    {"error": "NS instance (id: {}) was not found".format(
                         nsi_id),
                     "status": HttpCode.NOT_FOUND})
            nss.append(result)
        return {"ns": list(map(
            lambda x: self.filter_output_nsi(x), nss))}

    def filter_output_nsi(self, nsi):
        out_nsi = {}
        if "_id" not in nsi:
            raise osm_exception.OSMInstanceNotFound(
                    {"error": "NS instance was not found",
                     "status": HttpCode.NOT_FOUND})
        vim = nsi.get("vld")[0].get("vim_info")
        vim_id = None
        if vim is not None:
            for vim_k, vim_v in vim.items():
                vim_id = vim_v.get("vim_account_id")
                break
        vim_name = None
        vim_detail = self.get_vim_account(vim_id)
        if vim_detail is not None and "name" in vim_detail.keys():
            vim_name = vim_detail.get("name")
        creation_time = TimeHandling.ms_to_rfc3339(nsi.get("create-time"))
        out_nsi.update({
            "creation-time": creation_time,
            "ns-id": nsi.get("id"),
            "vnfd-id": nsi.get("vnfd-id"),
            "ns-name": nsi.get("name"),
            "status": {
                "config": nsi.get("config-status"),
                "operational": nsi.get("operational-status")
            }
        })
        vim_dict = {}
        if vim_id is not None:
            vim_dict.update({"id": vim_id})
        if vim_name is not None:
            vim_dict.update({"name": vim_name})
        if len(vim_dict) > 0:
            out_nsi.update({"vim": vim_dict})
        return out_nsi

    # Called externally
    @check_authorization
    def get_vnf_instances(self, vnfi_id=None):
        vnfs = []
        if vnfi_id is None:
            url = self.url_vnfr_detail
            response = requests.get(url,
                                    headers=self.headers,
                                    verify=False)
            vnfs = response.json()
        else:
            url = "{0}/{1}".format(self.url_vnfr_detail, vnfi_id)
            response = requests.get(url,
                                    headers=self.headers,
                                    verify=False)
            result = response.json()
            if result.get("status") == 404:
                raise osm_exception.OSMInstanceNotFound(
                    {"error": "VNF instance (id: {}) was not found".format(
                         vnfi_id),
                     "status": HttpCode.NOT_FOUND})
            vnfs.append(result)
        return {"vnf": list(map(
            lambda x: self.filter_output_vnfi(x), vnfs))}

    @check_authorization
    def filter_output_vnfi(self, vnfi):
        out_vnfi = {}
#        vnfd = self.get_vnf_descriptor(vnfi.get("vnfd-ref"))
        xdur = {}
        if len(vnfi.get("vdur")) > 0:
            xdur = vnfi.get("vdur")[0]
        elif len(vnfi.get("kdur")) > 0:
            xdur = vnfi.get("kdur")[0]
        ip = xdur.get("ip-address")
        if ip is None:
            for svc in xdur.get("services"):
                # Assumption: the main node will have to
                # communicate outwards, e.g., with LoadBalancer
                if svc.get("type") == "LoadBalancer":
                    ip = svc.get("cluster_ip")
        vim = self.get_vim_account(vnfi.get("vim-account-id"))
        ns_id = vnfi.get("nsr-id-ref")
        ns_name = self.get_ns_instance_name(ns_id)
        creation_time = TimeHandling.ms_to_rfc3339(vnfi.get("created-time"))
        out_vnfi.update({
            "creation-time": creation_time,
            "vnf-id": vnfi.get("id"),
            "vnfd-id": vnfi.get("vnfd-ref"),
            "ns-id": ns_id,
            "ns-name": ns_name,
            "ip": ip,
            "status": {
                "config": xdur.get("status"),
                "operational": vnfi.get("_admin").get("nsState")
            },
            "vim": {
                "id": vim.get("_id"),
                "name": vim.get("name"),
            }
        })
        try:
            out_vnfi.update({
                "k8scluster": {
                    "id": xdur.get("k8s-cluster").get("id"),
                    "namespace": xdur.get("k8s-namespace"),
                }
            })
        except Exception:
            pass
        return out_vnfi

#    @check_authorization
#    def get_vnf_descriptor(self, vnf_name):
#        url = "{0}?name={1}".format(
#            self.url_vnfd_list, vnf_name)
#        response = requests.get(url,
#                                headers=self.headers,
#                                verify=False)
#        vnfds = json.loads(response.text)
#        target_vnfd = None
#        for vnfd in vnfds:
#            if vnfd["name"] == vnf_name:
#                target_vnfd = vnfd
#        return target_vnfd

    @check_authorization
    def get_vim_account(self, vim_account_id):
        url = "{0}".format(self.url_vim_list)
        response = requests.get(url,
                                headers=self.headers,
                                verify=False)
        vims = json.loads(response.text)
        target_vim = None
        for vim in vims:
            if str(vim.get("_id")) == str(vim_account_id):
                target_vim = vim
        return target_vim

    def get_instance_id_by_vnfr_id(self, instances, vnfr_id):
        LOGGER.info("Getting instance_id by vnf_id")
        LOGGER.info("VNFR_ID {0}".format(vnfr_id))
        for instance in instances:
            for vnf_instance in instance.get(
                    "constituent-vnf-instances", []):
                if vnf_instance.get("vnfr-id") == vnfr_id:
                    return instance.get("instance-id")

    @check_authorization
    def exec_builtin_action_on_ns(self, nsi_id, action_name):
        inst_url = "{0}/{1}".format(self.url_nsi_list, nsi_id)
        if action_name not in self.osm_builtin_actions:
            return {"error":
                    "Action {} is not available".format(action_name),
                    "status": HttpCode.METH_NOT_ALLOW}
        data = {}
        if action_name == "terminate":
            data = {"timeout_ns_terminate": 1,
                    "autoremove": False,
                    # NB: enabling the one below is likely a cause for errors
                    "skip_terminate_primitives": False
                    }
        elif action_name == "scale":
            data = {
                     "scaleType": "SCALE_VNF",
                     "timeout_ns_scale": 0,
                     "scaleVnfData": {
                       "scaleVnfType": "SCALE_IN",
                       "scaleByStepData": {
                         "scaling-group-descriptor": "",
                         "scaling-policy": "",
                         "member-vnf-index": ""
                       }
                     }
                   }
        response = requests.post(
            "{0}/{1}".format(inst_url, action_name),
            headers=self.headers,
            data=data,
            verify=False)
        output = response.json()
        http_code = output.get("status", HttpCode.ACCEPTED)
        detail = output.get("detail")
        # Act upon a failed status
        # ... Yet ignore conflict (i.e., NS in a terminated state)
        if http_code == 404:
            raise osm_exception.OSMResourceNotFound(
                    {"error": detail})
        if http_code >= 400 and http_code != 409:
            raise osm_exception.OSMException(
                    {"error": detail,
                     "status": http_code})
        return {"id": nsi_id, "status": http_code}

    @check_authorization
    def exec_action_on_ns(self, nsi_id, payload):
        # nsd = self.get_ns_descriptor(nsi_id)
        primitive_name = payload.get("action")
        primitive_params = payload.get("params")

        # First, enforce the NS instance exists
        url_nsi_details = "{}?id={}".format(self.url_nsi_detail, nsi_id)
        response = requests.get(url_nsi_details,
                                headers=self.headers,
                                verify=False)
        nsd = response._content
        if nsd is None:
            raise osm_exception.OSMResourceNotFound(
                {"error": "Cannot retrieve details for NS with " +
                          "ID={}".format(nsi_id)})

        # If action is one of the predetermined actions, call the specific
        # endpoint (no params required) and finish
        if primitive_name in self.osm_builtin_actions:
            return self.exec_builtin_action_on_ns(nsi_id, primitive_name)

        # Otherwise, obtain the NS descriptor for the VNF package name,
        # then inspect its KDUs
        nsd = response.json()
        instance_url = self.url_nsd_action.format(nsi_id)
        vnfd_name = nsd[0].get("nsd").get("vnfd-id")
        if isinstance(vnfd_name, list):
            vnfd_name = vnfd_name[0]
        response = requests.get("{}?id={}".format(
            self.url_vnfd_list, vnfd_name),
                                headers=self.headers,
                                verify=False)
        vnfd = response._content
        if vnfd is None:
            raise osm_exception.OSMPackageError(
                {"error": "Cannot retrieve suitable NF for NS package " +
                          "with name={}".format(vnfd_name),
                 "status": HttpCode.NOT_FOUND})
        vnfd = response.json()
        if isinstance(vnfd, list):
            vnfd = vnfd[0]
        vnfd_member_vnf = vnfd.get("id")

        # Iterate on all existing KDUs
        for vnfd_kdu in vnfd.get("kdu"):
            vnfd_kdu_name = vnfd_kdu.get("name")
            try:
                primitive_params = json.loads(primitive_params)
            except Exception:
                pass
            osm_payload = {
                "kdu_name": vnfd_kdu_name,
                "member_vnf_index": vnfd_member_vnf,
                "primitive": primitive_name,
                "primitive_params": primitive_params
            }
            resp = requests.post(
                instance_url,
                headers=self.headers,
                data=yaml_dump(osm_payload),
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
            output = resp.json()
            status_code = output.get("status")
            if status_code is None:
                status_code = HttpCode.ACCEPTED
            if status_code >= 200 and status_code < 400:
                success_msg = {"ns-id": nsi_id,
                               "action-name": primitive_name,
                               "action-params": primitive_params,
                               "status": status_code}
                return success_msg
            else:
                error_msg = {"status": status_code,
                             "error": output.get("detail")}
                return error_msg
