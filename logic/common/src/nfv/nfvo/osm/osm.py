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
from common.events.kafka.producer import SOProducer
from common.log.log import setup_custom_logger
from common.messages.actions import ACTION_STATUS
from common.schemas.lcm_ns import NSInstanceActionExecWaitForData
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
        self.so_section = self.nfvo_category.get("so")
        self.so_ip = self.so_section.get("ip")
        self.osm_section = self.nfvo_category.get("osm")
        self._read_cfg_osm(self.osm_section)
        self._create_ep_osm()
        self._create_session()
        # Get ports for services
        self.catalogue_modules = self.config.get("modules.yaml")
        self.catalogue_module = self.catalogue_modules.get("modules")
        self.timings_section = self.nfvo_category.get("timings")
        self._read_cfg_timings(self.timings_section)
        self._read_cfg_xnfs(self.nfvo_category.get("xnfs"))
        # Definition of expected/target status upon operations
        self.deployment_expected_status = "running"
        self.deletion_expected_status = "terminated"
        self.action_expected_status = "completed"
        self.force_deletion_expected_status = "failed"
        # self.osm_builtin_actions = ["initiate", "scale",
        #    "terminate", "update"]
        self.osm_builtin_actions = ["instantiate", "scale", "terminate"]
        # Message broker
        self._read_cfg_events(self.nfvo_category.get("events"))

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

    def _read_cfg_timings(self, cfg_section: dict):
        self.timing_interval = cfg_section.get("interval")
        self.async_to_sec = cfg_section.get("timeout")
        self.timing_to = self.async_to_sec.get("default")
        self.timing_to_inst = self.async_to_sec.get("instantiation")
        self.timing_to_act = self.async_to_sec.get("action")
        self.timing_to_sca = self.async_to_sec.get("scale")
        self.timing_to_term = self.async_to_sec.get("termination")
        self.timing_to_del = self.async_to_sec.get("deletion")

    def _read_cfg_events(self, cfg_section: dict):
        try:
            self.events_active = bool(cfg_section.get("active"))
        except Exception:
            self.events_active = False
        self.topics_section = cfg_section.get("topics")
        self.events_topics_inst_ae = self.topics_section.get(
            "instantiation-ae")
        self.events_topics_acts_portal = self.topics_section.get(
            "actions-portal")

    def _read_cfg_xnfs(self, cfg_section: dict):
        cfg_xnfs_gen = cfg_section.get("general")
        self.xnf_user = cfg_xnfs_gen.get("user")
        try:
            curr_path = os.path.dirname(os.path.abspath(__file__))
            key_path = os.path.join(curr_path, "../../../../keys")
            with open("{}/{}".format(
                  key_path, cfg_xnfs_gen.get("ssh-key"))) as fhandle:
                self.xnf_key = fhandle.read()
        except Exception as e:
            raise osm_exception.OSMXNFKeyNotFound(e)

    def _create_ep_osm(self):
        def _ep(url):
            # Note: initial "/" shall be provided in "url"
            return "{0}/osm{1}".format(self.base_url, url)

        # Authentication
        self.url_token = _ep("/admin/v1/tokens")
        # Package descriptors (NSD, xNFD)
        self.url_nsd_list = _ep("/nsd/v1/ns_descriptors")
        self.url_nsd_detail = _ep("/nsd/v1/ns_descriptors_content")
        self.url_xnfd_list = _ep("/vnfpkgm/v1/vnf_packages")
        self.url_xnfd_detail = _ep("/vnfpkgm/v1/vnf_packages_content")
        # Running instances (NSI, xNFI) and actions (on NSs)
        self.url_nsi_list = _ep("/nslcm/v1/ns_instances")
        self.url_nsi_detail = _ep("/nslcm/v1/ns_instances_content")
        self.url_nsd_action = _ep("/nslcm/v1/ns_instances/{}/action")
        # Actions on running instances (NSI)
        self.url_nsi_action_detail = _ep("/nslcm/v1/ns_lcm_op_occs")
        # Records of running instances (NSR, xNFR)
        self.url_xnfr_detail = _ep("/nslcm/v1/vnfrs")
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

    # Events / alerts

    def notify_message_broker(self, topic, event_data):
        ev_producer = SOProducer(topic)
        ev_producer.write(event_data)

    def notify_message_broker_portal(self, action_name, description, ips):
        if not isinstance(ips, list):
            ips = [ips]
        data = {
                "componentType": "sco",
                "componentId": "so",
                "componentIP": self.so_ip,
                "actionName": action_name,
                "actionDescription": description,
                "onIps": ips
                }
        self.notify_message_broker(self.events_topics_acts_portal, data)

    def notify_message_broker_ae(self, nsi_id):
        infra_url = "http://{}:{}/mon/infra/service?id={}".format(
                    "so-mon",
                    self.catalogue_module.get("mon").get("port"),
                    nsi_id)
        response = requests.get(infra_url, verify=False)
        infra_data = response.json()
        # Filter infrastructure with non-existing services
        infra_data = infra_data.get("infrastructures")
        if isinstance(infra_data, list):
            infra_data = list(filter(
                lambda x: len(x.get("ns")) > 0,
                infra_data))
            infra_data = list(filter(
                lambda x: nsi_id in
                [x_.get("ns-id") for x_ in x.get("ns")],
                infra_data))
        else:
            infra_data = list(filter(
                lambda x: len(x) > 0,
                infra_data.get("ns")))
            infra_data = list(filter(
                lambda x: nsi_id == x.get("ns-id"),
                infra_data))
        if len(infra_data) > 0:
            infra_data = infra_data[0]
        if infra_data is not None:
            self.notify_message_broker(self.events_topics_inst_ae,
                                       infra_data)

    def notify(self, trigger_modes: str, event_msg: str, **kwargs):
        """
        Notify the successful execution of one or more actions
        (i.e. "trigger_modes) to all involved components
        """
        if self.events_active:
            trigger_mode = trigger_modes[0]
            xni_ip = kwargs.get("xni-ip")
            nsi_id = kwargs.get("nsi-id")

            if len(trigger_modes) == 1 and (
                "deployment" in trigger_modes or
                    "deletion" in trigger_modes):
                # Notify Portal
                t = threading.Thread(target=self.notify_message_broker_portal,
                                     args=(trigger_mode,
                                           event_msg,
                                           xni_ip))
                t.start()

            if "deployment" in trigger_modes:
                # Notify TAR/AE
                # (in case of trigger_modes=["deployment"]
                # or trigger_modes=["deployment", "action"]
                # NB: the comma must be provided after the argument,
                # otherwise it will somehow attempt to decompress
                t = threading.Thread(target=self.notify_message_broker_ae,
                                     args=(nsi_id,))
                t.start()

            trigger_mode_action = None
            for mode in trigger_modes:
                if mode.startswith("action."):
                    trigger_mode_action = mode.replace("action.", "")
                    break
                if mode.startswith("action"):
                    trigger_mode_action = "action"
                    break
            if trigger_mode_action is not None:
                # Notify Portal
                t = threading.Thread(target=self.notify_message_broker_portal,
                                     args=(trigger_mode_action,
                                           event_msg,
                                           xni_ip))
                t.start()

            if len(trigger_modes) == 1 and (
                "onboarding" in trigger_modes or
                    "deboarding" in trigger_modes):
                # Notify Portal
                t = threading.Thread(target=self.notify_message_broker_portal,
                                     args=(trigger_mode,
                                           event_msg,
                                           []))
                t.start()

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
    def get_xnf_descriptor(self, xnf_filter):
        """
        Given a name (or ID), returns the xNFD.
        """
        response = requests.get(self.url_xnfd_list,
                                headers=self.headers,
                                verify=False)
        xnfds = json.loads(response.text)
        for xnfd in xnfds:
            if xnfd.get("name", None) == xnf_filter or\
                    xnfd.get("product-name", None) == xnf_filter or\
                    xnfd.get("_id", None) == xnf_filter:
                return xnfd
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
    def get_xnf_descriptors(self, xnf_filter=None):
        response = requests.get(self.url_xnfd_list,
                                headers=self.headers,
                                verify=False)
        xnfs = json.loads(response.text)
        result = xnfs
        if xnf_filter is not None and not isinstance(xnf_filter, list):
            xnfd = self.get_xnf_descriptor(xnf_filter)
            if xnfd is None:
                raise osm_exception.OSMPackageError(
                    {"error": "Package {} does not exist".format(xnf_filter),
                     "status": HttpCode.NOT_FOUND})
            result = xnfd
        if not isinstance(result, list):
            result = [result]
        return {
            "xnf": list(map(lambda x: self.filter_output_xnfd(x), result)),
            "status": HttpCode.OK}

    def filter_output_nsd(self, nsd):
        out_nsd = {}
        out_nsd["name"] = nsd.get("id")
        out_nsd["id"] = nsd.get("_id")
        out_nsd["description"] = nsd.get("description")
        out_nsd["provider"] = \
            nsd.get("designer",
                    nsd.get("provider",
                            nsd.get("vendor", None)))
        out_nsd["version"] = nsd.get("version", None)
        out_nsd["xnfs"] = nsd.get("vnfd-id")
        out_nsd["virtual-links"] = [
            x["id"] for x in nsd.get("virtual-link-desc", [])
            ]
        return out_nsd

    def filter_output_xnfd_action(self, xnf_action_block):
        primitives = []
        if xnf_action_block is None:
            return primitives
        for action in xnf_action_block:
            prim = {
                "name": action.get("name"),
                "parameter": {},
            }
            if action.get("parameter") is None:
                continue
            for action_param in action.get("parameter"):
                param_value = action_param.get("value")
                if param_value is None:
                    param_value = action_param.get("default-value")
                prim["parameter"].update({
                    "name": action_param.get("name"),
                    "type": action_param.get("data-type"),
                    "value": param_value,
                })
            primitives.append(prim)
        return primitives

    def filter_output_xnfd(self, xnf):
        out_xnfd = {}
        out_xnfd["name"] = xnf.get("id")
        out_xnfd["id"] = xnf.get("_id")
        out_xnfd["description"] = xnf.get("description")
        out_xnfd["provider"] = \
            xnf.get("designer",
                    xnf.get("provider",
                            xnf.get("vendor", None)))
        out_xnfd["version"] = xnf.get("version", None)
        try:
            xnf_lcm_ops_cfg = \
                    xnf.get("df", [{}])[0]["lcm-operations-configuration"]
            xnf_lcm_xnf_ops_cfg = xnf_lcm_ops_cfg.get("operate-vnf-op-config")
            xnf_lcm_xnf_ops_day12_cfg = xnf_lcm_xnf_ops_cfg.get("day1-2")
            day0_prims = self.filter_output_xnfd_action(
                    xnf_lcm_xnf_ops_day12_cfg[0].get(
                        "initial-config-primitive"))
            day12_prims = self.filter_output_xnfd_action(
                    xnf_lcm_xnf_ops_day12_cfg[0].get(
                        "config-primitive"))
            out_xnfd["config-actions"] = {
                "day0": day0_prims, "day1-2": day12_prims
                }
        except Exception:
            out_xnfd["config-actions"] = []
        try:
            xnf_inst_level = xnf.get("df")[0]["instantiation-level"]
            xnf_vdu_struct = xnf_inst_level[0]["vdu-level"][0]
            out_xnfd["vdus"] = xnf_vdu_struct.get("number-of-instances")
        except Exception:
            out_xnfd["vdus"] = 0
        nss = self.get_ns_descriptors()
        for ns in nss["ns"]:
            for cxnf in ns.get("constituent-vnfs", []):
                if cxnf["vnfd-id-ref"] == xnf.get("name"):
                    out_xnfd["ns-name"] = ns.get("ns-name")
        return out_xnfd

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
    def upload_package(self, bin_file, url, pkg_type):
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

        pkg_id = output.get("id")
        trigger_modes = ["onboarding"]
        event_msg = "SC package with id={0} has been onboarded".\
            format(pkg_id)
        event_args = {"xni-ip": []}
        self.notify(trigger_modes, event_msg, **event_args)

        return {
            "{}-pkg-id".format(pkg_type): pkg_id,
            "status": HttpCode.ACCEPTED}

    def upload_xnfd_package(self, bin_file):

        # # TODO: remove
        # print("xnf bin_file={}".format(bin_file))
        # error_upload = False
        # pkg_name = "snort_cnf"
        # try:
        #     if bin_file is None:
        #         # Hardcoded value, remember to have the package on
        #         # the container and to have it updated
        #         pkg_path = "{}.tar.gz".format(pkg_name)
        #         if os.path.isfile(pkg_path):
        #             fp = open(pkg_path, "rb")
        #             filename = os.path.basename(pkg_path)
        #             mime = MimeTypes()
        #             content_type = mime.guess_type(pkg_path)
        #             bin_file = FileStorage(
        #                 fp, filename, "package", content_type)
        #         else:
        #             error_upload = True
        # except Exception:
        #     error_upload = True

        # TODO: uncomment
        # Endpoint: "/xnfpkgm/v1/xnf_packages_content"
        return self.upload_package(bin_file, self.url_xnfd_detail, "xnf")
        # if error_upload:
        #     existing_xnfd = self.get_xnf_descriptor(pkg_name)
        #     existing_xnfd_id = existing_xnfd.get("_id")
        #     print("Package={} has ID={}".format(pkg_name, existing_xnfd_id))
        #     return {"xnf-pkg-id": existing_xnfd_id}
        # else:
        #     return self.upload_package(bin_file, self.url_xnfd_detail, "xnf")

    def upload_nsd_package(self, bin_file):

        # TODO: remove
        # print("nsd bin_file={}".format(bin_file))
        # error_upload = False
        # pkg_name = "snort_ns"
        # try:
        #     if bin_file is None:
        #         # Hardcoded value, remember to have the package on
        #         # the container and to have it updated
        #         pkg_path = "{}.tar.gz".format(pkg_name)
        #         if os.path.isfile(pkg_path):
        #             fp = open(pkg_path, "rb")
        #             filename = os.path.basename(pkg_path)
        #             mime = MimeTypes()
        #             content_type = mime.guess_type(pkg_path)
        #             bin_file = FileStorage(
        #                 fp, filename, "package", content_type)
        #         else:
        #             error_upload = True
        # except Exception:
        #     error_upload = True

        # # TODO: uncomment
        # Endpoint: "/nsd/v1/ns_descriptors_content"
        return self.upload_package(bin_file, self.url_nsd_detail, "ns")
        # if error_upload:
        #     existing_nsd = self.get_ns_descriptor(pkg_name)
        #     existing_nsd_id = existing_nsd.get("_id")
        #     print("Package={} has ID={}".format(pkg_name, existing_nsd_id))
        #     return {"ns-pkg-id": existing_nsd_id}
        # else:
        #     return self.upload_package(bin_file, self.url_nsd_detail, "ns")

    def guess_descriptor_type(self, package_name):
        res = {}
        descriptor_id = None
        descriptor = self.get_xnf_descriptor(package_name)
        if descriptor is not None:
            descriptor_id = descriptor.get("_id")
            res.update({"id": descriptor_id, "type": "xnf"})
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
                    return "xnfd"
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
            if ptype == "xnfd":
                output = self.upload_xnfd_package(bin_file)
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
        elif descriptor_type == "xnf":
            del_url = "{0}/{1}".format(
                self.url_xnfd_list,
                descriptor_id)
        else:
            raise osm_exception.OSMUnknownPackageType(
                    "Package {} with unknown type".format(package_name))
        response = requests.delete("{0}".format(del_url),
                                   headers=self.headers,
                                   verify=False)
        if response.status_code >= 200 and response.status_code < 300:
            trigger_modes = ["deboarding"]
            event_msg = "SC package with id={0} has been deboarded".\
                format(descriptor_id)
            event_args = {"xni-ip": []}
            self.notify(trigger_modes, event_msg, **event_args)
            return {
                "name": package_name, "pkg-id": descriptor_id,
                "status": response.status_code}
        elif response.status_code == 409:
            parsed_error, status = OSMResponseParsing.parse_failed(response)
            parsed_error = parsed_error.get("error", parsed_error)
            raise osm_exception.OSMPackageConflict(
                    {"error": parsed_error, "status": status})
        else:
            parsed_error, status = OSMResponseParsing.parse_failed(response)
            raise osm_exception.OSMException({
                    "error": parsed_error.get("error", parsed_error),
                    "status": status or HttpCode.INTERNAL_ERROR})

    # Running instances

    # Called externally
    @check_authorization
    def fetch_actions_data(self, nsi_id: str, action_id: str = None):
        actions_ret = {"ns": nsi_id, "actions": []}
        url_nsi_details = "{}/?nsInstanceId={}".format(
                              self.url_nsi_action_detail, nsi_id)
        response = requests.get(url_nsi_details,
                                headers=self.headers,
                                verify=False)
        actions_resp = response.json()
        if actions_resp is None or actions_resp == []:
            raise osm_exception.OSMResourceNotFound({
                "error": "NS with id={} does not exist".format(nsi_id)
                + " or has not received action requests"})
        actions_ret_list = []
        for action in actions_resp:
            action_type = action.get("lcmOperationType")
            if action_type != "action":
                action_type = "built-in ({})".format(action_type)
            action_status = action.get("operationState")
            if action_status is not None:
                action_status = action_status.lower()
            action_exec_time = TimeHandling.ms_to_rfc3339(
                    action.get("startTime"))
            action_ret = {
                    "id": action.get("_id"),
                    "start-time": action_exec_time,
                    "type": action_type,
                    "params": action.get("operationParams"),
                    "status": action_status,
                    "detailed-status": action.get("detailed-status"),
            }
            if action_status == "failed":
                action_ret.update({
                    "error": action.get("errorMessage")})
            if action_id is not None:
                if action_id == action_ret.get("id"):
                    actions_ret_list = [action_ret]
                    break
            else:
                actions_ret_list.append(action_ret)
        actions_ret.update({"actions": actions_ret_list})
        return {"status": HttpCode.OK, **actions_ret}

    def monitor_ns_action(self, nsi_id: str, action_id: str,
                          target_status=None):
        timeout = self.timing_to_act
        action_executed = False
        while not action_executed:
            try:
                action = self.fetch_actions_data(nsi_id, action_id)
            except osm_exception.OSMException:
                LOGGER.info("No action found, aborting data fetching")
                break
            if timeout < 0:
                LOGGER.info("Timeout reached, aborting thread")
                break
            if action is None:
                LOGGER.info("No action found, aborting thread")
                break
            operational_status = action.get("actions", [None])[0].get("status")
            if operational_status is not None:
                operational_status = operational_status.lower()
            LOGGER.debug("Operational status (action): {0} ...".format(
                operational_status))
            # When target is met and action has been executed...
            if operational_status == self.action_expected_status:
                action_executed = True
            if not action_executed:
                sleep(self.timing_interval)
                timeout = timeout-self.timing_interval
        return action_executed

    # Called externally
    def apply_action(self, nsi_id, inst_md, wait_for=None, **kwargs):
        if nsi_id is None:
            raise osm_exception.OSMInstanceNotFound(
                {"error": "NS instance (id: {}) was not found".format(
                     nsi_id),
                 "status": HttpCode.NOT_FOUND})

        action_name = inst_md.get("ns-action-name")
        if action_name is None:
            raise osm_exception.OSMException(
                {"error": "Missing action name",
                 "status": HttpCode.PARTIAL_CONTENT})
        # If no action params are provided, use empty ones by default
        action_params = inst_md.get("ns-action-params", {})

        # By default this is an asynchronous method
        # But it can be configured otherwise, called by the client with
        # the query param "wait-for" set to any of these values:
        #   - (0) NONE: nothing to wait for, async method
        #   - (1) ACTION_ID: just wait enough to get the action ID
        #   - (1, 2) ACTION_OUTPUT: wait for action to finish and return output
        wait_for_none = wait_for == NSInstanceActionExecWaitForData.none
        wait_for_action_id = wait_for == \
            NSInstanceActionExecWaitForData.action_id
        wait_for_action_output = wait_for == \
            NSInstanceActionExecWaitForData.action_output
        # Enforce the default option if none was selected
        if not any(
                [wait_for_none, wait_for_action_id, wait_for_action_output]):
            wait_for_none = True

        # Check whether NS instance exists
        nss = self.get_ns_instances(nsi_id)
        if len(nss.get("ns")) == 0:
            raise osm_exception.OSMInstanceNotFound(
                {"error": "NS with id={} does not exist".format(nsi_id)})

        trigger_modes = ["action"]
        # If the NS instance exists, trigger the action
        target_status = self.deployment_expected_status
        if self.deployment_expected_status in inst_md:
            target_status = inst_md.get("target_status")
        # Passing also current_app._get_current_object() (flask global context)
        LOGGER.debug("[DEBUG] Launching thread to monitor status " +
                     "prior to applying action")

        if wait_for_none:
            t = threading.Thread(target=self.monitor_ns_deployment_and_act,
                                 args=(nsi_id,
                                       action_name,
                                       action_params,
                                       trigger_modes,
                                       current_app._get_current_object(),
                                       target_status))
            t.start()
            # output = {
            #     "status": HttpCode.ACCEPTED,
            #     "id": nsi_id,
            #     **inst_md
            # }
            output = dict(ACTION_STATUS)
            output["ns-id"] = nsi_id
            output["ns-action-name"] = action_name
            output["ns-action-params"] = action_params
            output["ns-action-status"] = "processing"
            output["status"] = HttpCode.ACCEPTED
        # (1) The first part is common whether waiting for the action
        # ID or its full output
        elif wait_for_action_id or wait_for_action_output:
            ns_deployed = False
            while not ns_deployed:
                ns_deployed = self.monitor_ns_deployment(
                    nsi_id, current_app._get_current_object(),
                    trigger_modes, target_status)
            # Execute action only if any provided
            action_name = inst_md.get("ns-action-name")
            payload = {"action": action_name,
                       "params": action_params}
            # Execute the specific action at the NS instance
            output = self.exec_action_on_ns(nsi_id, payload)

        # (2) The second part requires monitoring whether the action
        # has finished and retrieve its outcome
        if wait_for_action_output:
            # Get data from the submitted actions to pick the action-id
            submitted_actions = self.fetch_actions_data(nsi_id)
            # Actions seem to be ordered
            action = submitted_actions.get("actions")[-1]
            action_id = action.get("id")
            action_name = action.get("params", {}).get("primitive")
            self.monitor_ns_action(nsi_id, action_id)
            # Get status for this particular action
            submitted_action = self.fetch_actions_data(nsi_id, action_id)
            submitted_action = submitted_action.get("actions")[0]
            action_status = submitted_action.get("status")
            action_det_status = submitted_action.get("detailed-status")
            output.update({
                "ns-action-status": action_status,
                "ns-action-status-detailed": action_det_status,
            })
        return output

    def monitor_ns_deployment(self, nsi_id, app, trigger_modes,
                              target_status=None):
        output = {"status": HttpCode.ACCEPTED}
        timeout = self.timing_to_inst
        ns_deployed = False
        nss = {}
        if target_status is None:
            target_status = self.deployment_expected_status
        while not ns_deployed:
            try:
                nss = self.get_ns_instances(nsi_id)
            except osm_exception.OSMException:
                LOGGER.info("No instance found, aborting configuration")
                break
            if timeout < 0:
                LOGGER.info("Timeout reached, aborting thread")
                break
            if nss is None:
                LOGGER.info("No instance found, aborting thread")
                break
            # operational_status = nss.get("operational-status", "")
            operational_status = nss.get("ns")[0].get("status")\
                                    .get("operational")
            LOGGER.debug("Operational status (deployment): {0} ...".format(
                operational_status))
            if "failed" == operational_status:
                LOGGER.info("Instance failed, aborting")
                output.update({
                    "status": HttpCode.INTERNAL_ERROR,
                    "error": "NS instance {} is in failed state".format(nsi_id)
                })
                break
            # When target is met and NS instance is running...
            if target_status == operational_status:
                ns_deployed = True
                break
            if not ns_deployed:
                sleep(self.timing_interval)
                timeout = timeout-self.timing_interval
        # Notify if finally deployed (if this is the monitored action)
        if ns_deployed and "deployment" in trigger_modes:
            # Retrieve details on NS and xNF
            nsi_details = self.get_ns_instance_details(nsi_id)
            xni_ip = nsi_details.get("ip-infra")
            # xni_id = nss.get("ns")[0].get("xnf").get("id")
            # if isinstance(xni_id, list):
            #     xni_id = xni_id[0]
            # xni_data = self.get_xnf_instances(xni_id)
            # xni_ip = xni_data.get("xnf")[0].get("ip")
            event_msg = "SC with id={0} has been deployed".\
                format(nsi_id)
            event_args = {
                "xni-ip": xni_ip,
                "nsi-id": nsi_id,
            }
            self.notify(trigger_modes, event_msg, **event_args)
        return ns_deployed

    def monitor_ns_deployment_and_act(self, nsi_id, action_name,
                                      action_params, trigger_modes, app,
                                      target_status=None):
        ns_deployed = False
        while not ns_deployed:
            ns_deployed = self.monitor_ns_deployment(
                nsi_id, app, trigger_modes, target_status)
        payload = {"action": action_name,
                   "params": action_params}
        # Execute the specific action at the NS instance
        output = self.exec_action_on_ns(nsi_id, payload)

#        if action_name is not None:
#            app.mongo.store_xnf_action(xnf_instance,
#                                       action_name,
#                                       action_params,
#                                       json.loads(output))
        LOGGER.info(
            "Action performed and stored, exiting thread")
        return output

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
                      .format(vim_id)})
        elif status_code == 404:
            if "any nsd with filter" in detail:
                raise osm_exception.OSMResourceNotFound(
                    {"error": "NS package with id={} does not exist"
                        .format(ns_pkg_id)})
        elif status_code > 400:
            raise osm_exception.OSMException(
                {"error": detail, "status": status_code})

        nsr_id = response_data.get("id")

        trigger_modes = ["deployment"]
        if ns_action_name is not None:
            trigger_modes.append("action")

        # Asynchronous behaviour
        t = threading.Thread(target=self.monitor_ns_deployment_and_act,
                             args=(nsr_id, ns_action_name, ns_action_params,
                                   trigger_modes,
                                   current_app._get_current_object(),
                                   self.deployment_expected_status))
        t.start()
        if status_code >= 200 and status_code < 400:
            success_msg = {"name": ns_name,
                           "ns-id": response_data.get("id"),
                           "ns-pkg-id": ns_pkg_id,
                           "status": HttpCode.ACCEPTED}
            if nsi_data.get("nsDescription") is not None:
                success_msg["description"] = nsi_data.get("nsDescription")
            if nsi_data.get("vimAccountId") is not None:
                success_msg["vim-id"] = nsi_data.get("vimAccountId")
            if nsi_data.get("ssh_keys") is not None:
                success_msg["ssh-keys"] = nsi_data.get("ssh_keys")
            if ns_action_name is not None:
                success_msg["ns-action-name"] = ns_action_name
            if ns_action_params is not None:
                success_msg["ns-action-params"] = ns_action_params
            return success_msg
        else:
            error_msg = {"status": response_data.status.code,
                         "error": detail}
            return error_msg

    @check_authorization
    def delete_ns_instance(self, nsr_id, force=False):
        self.exec_builtin_action_on_ns(nsr_id, "terminate")
        # Asynchronous behaviour
        t = threading.Thread(target=self.monitor_ns_deletion,
                             args=(nsr_id, force))
        t.start()
        return {"ns-id": nsr_id, "status": HttpCode.ACCEPTED}

    @check_authorization
    def monitor_ns_deletion(self, nsi_id, force=False):
        timeout = self.timing_to_del
        ns_deleted = False
        inst_url = "{0}/{1}".format(self.url_nsi_list,
                                    nsi_id)

        # Retrieve details on NS and xNF
        nsi_details = self.get_ns_instance_details(nsi_id)
        xni_ip = nsi_details.get("ip-infra")

        while timeout > 0:
            try:
                ns_status = self.get_ns_instances(nsi_id)
                status = ns_status.get("ns")[0].get("status")\
                    .get("operational").lower()
                LOGGER.info("Monitoring status for ns={0}: {1}".format(
                    nsi_id, status))
                if status in [self.deletion_expected_status,
                              self.force_deletion_expected_status]:
                    ns_deleted = True
                    LOGGER.info("NS with id={0} already in state={1}".format(
                        nsi_id, status))
                    trigger_modes = ["deletion"]
                    event_msg = "SC with id={0} has been deleted".\
                        format(nsi_id)
                    event_args = {"xni-ip": xni_ip}
                    self.notify(trigger_modes, event_msg, **event_args)
                    break
            except Exception as e:
                LOGGER.error("Cannot retrieve status for ns={0}. Details={1}".
                             format(nsi_id, e))
                break
            if not ns_deleted:
                timeout -= self.timing_interval
                # sleep(1)
                sleep(self.timing_interval)
        if force:
            inst_url = "{}?FORCE=true".format(inst_url)
        delete = requests.delete(inst_url,
                                 headers=self.headers,
                                 verify=False)
        LOGGER.info("Terminating {0}".format(delete.text))

    @check_authorization
    def get_ns_instance_details(self, nsi_id):
        # First, enforce the NS instance exists
        url_nsi_details = "{}?id={}".format(self.url_nsi_detail, nsi_id)
        response = requests.get(url_nsi_details,
                                headers=self.headers,
                                verify=False)
        nsi_det = response._content
        if nsi_det is None:
            raise osm_exception.OSMResourceNotFound(
                {"error": "Cannot retrieve details for NS with " +
                          "ID={}".format(nsi_id)})
        # Otherwise, obtain the NS descriptor for the xNF package name,
        # then inspect its KDUs
        nsi_det = response.json()
        xni_ip = "N/A"
        try:
            vca_status = list(nsi_det[0].get("vcaStatus").values())[0]
            vca_apps = list(vca_status.get("applications").values())[0]
            vca_units = list(vca_apps.get("units").values())[0]
            xni_ip = vca_units.get("address")
        except Exception:
            pass
        nsi_ret = {
            "nsi": nsi_det,
            "ip-infra": xni_ip,
        }
        return nsi_ret

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
        nsi_id = nsi.get("id")
        out_nsi.update({
            "creation-time": creation_time,
            "id": nsi_id,
            "name": nsi.get("name"),
            "package": {
                "id": nsi.get("nsd-id"),
                "name": nsi.get("nsd-ref"),
            },
            "xnf": {
                "id": nsi.get("constituent-vnfr-ref"),
                # "xnfd-id": nsi.get("vnfd-id"),
            },
            "status": {
                "config": nsi.get("config-status"),
                "operational": nsi.get("operational-status")
            }
        })
        actions = {}
        try:
            vca_apps = nsi.get("vcaStatus").get(nsi_id).get("applications")
            for vca_app_name, vca_app_cfg in vca_apps.items():
                actions.update(vca_app_cfg.get("actions"))
        except Exception:
            pass
        if len(actions) > 0:
            out_nsi.update({"actions": actions})
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
    def get_xnf_instances(self, xnfi_id=None):
        xnfs = []
        if xnfi_id is None:
            url = self.url_xnfr_detail
            response = requests.get(url,
                                    headers=self.headers,
                                    verify=False)
            xnfs = response.json()
        else:
            url = "{0}/{1}".format(self.url_xnfr_detail, xnfi_id)
            response = requests.get(url,
                                    headers=self.headers,
                                    verify=False)
            result = response.json()
            if result.get("status") == 404:
                raise osm_exception.OSMInstanceNotFound(
                    {"error": "xNF instance (id: {}) was not found".format(
                         xnfi_id),
                     "status": HttpCode.NOT_FOUND})
            xnfs.append(result)
        return {"xnf": list(map(
            lambda x: self.filter_output_xnfi(x), xnfs))}

    @check_authorization
    def filter_output_xnfi(self, xnfi):
        out_xnfi = {}
#        xnfd = self.get_xnf_descriptor(xnfi.get("xnfd-ref"))
        xdur = {}
        if len(xnfi.get("vdur")) > 0:
            xdur = xnfi.get("vdur")[0]
        elif len(xnfi.get("kdur")) > 0:
            xdur = xnfi.get("kdur")[0]
        ip = xdur.get("ip-address")
        if ip is None:
            for svc in xdur.get("services"):
                # Assumption: the main node will have to
                # communicate outwards, e.g., with LoadBalancer
                if svc.get("type") == "LoadBalancer":
                    ip = svc.get("cluster_ip")
        vim = self.get_vim_account(xnfi.get("vim-account-id"))
        ns_id = xnfi.get("nsr-id-ref")
        ns_name = self.get_ns_instance_name(ns_id)
        creation_time = TimeHandling.ms_to_rfc3339(xnfi.get("created-time"))
        out_xnfi.update({
            "creation-time": creation_time,
            "id": xnfi.get("id"),
            "package": {
                "id": xnfi.get("vnfd-id"),
                "name": xnfi.get("vnfd-ref"),
            },
            "ns": {
                "id": ns_id,
                "name": ns_name,
            },
            "ip": ip,
            "status": {
                "config": xdur.get("status"),
                "operational": xnfi.get("_admin").get("nsState")
            },
            "vim": {
                "id": vim.get("_id"),
                "name": vim.get("name"),
            }
        })
        try:
            out_xnfi.update({
                "k8scluster": {
                    "id": xdur.get("k8s-cluster").get("id"),
                    "namespace": xdur.get("k8s-namespace"),
                }
            })
        except Exception:
            pass
        return out_xnfi

#    @check_authorization
#    def get_xnf_descriptor(self, xnf_name):
#        url = "{0}?name={1}".format(
#            self.url_xnfd_list, xnf_name)
#        response = requests.get(url,
#                                headers=self.headers,
#                                verify=False)
#        xnfds = json.loads(response.text)
#        target_xnfd = None
#        for xnfd in xnfds:
#            if xnfd["name"] == xnf_name:
#                target_xnfd = xnfd
#        return target_xnfd

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

    def get_instance_id_by_xnfr_id(self, instances, xnfr_id):
        LOGGER.info("Getting instance_id by xnf_id")
        LOGGER.info("xNFR_ID {0}".format(xnfr_id))
        for instance in instances:
            for xnf_instance in instance.get(
                    "constituent-vnf-instances", []):
                if xnf_instance.get("vnfr-id") == xnfr_id:
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
            data = {
                    "timeout_ns_terminate": self.timing_to_act,
                    "autoremove": False,
                    "skip_terminate_primitives": True
                   }
        elif action_name == "scale":
            data = {
                     "scaleType": "SCALE_VNF",
                     "timeout_ns_scale": self.timing_to_sca,
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
        return {"ns-id": nsi_id, "status": http_code}

    @check_authorization
#    @test_topic(some="value")
    def exec_action_on_ns(self, nsi_id, payload):
        # nsd = self.get_ns_descriptor(nsi_id)
        primitive_name = payload.get("action")
        primitive_params = payload.get("params")

        # Retrieve details on NS and xNF
        nsi_details = self.get_ns_instance_details(nsi_id)

        if nsi_details is not None and len(nsi_details.get("nsi")) == 0:
            raise osm_exception.OSMInstanceNotFound(
                {"error": "Instance with id={} does not exist".format(nsi_id),
                 "status": HttpCode.NOT_FOUND})

        nsd = nsi_details.get("nsi")
        xni_ip = nsi_details.get("ip-infra")

        # If action is one of the predetermined actions, call the specific
        # endpoint (no params required) and finish
        if primitive_name in self.osm_builtin_actions:
            return self.exec_builtin_action_on_ns(nsi_id, primitive_name)

        instance_url = self.url_nsd_action.format(nsi_id)
        xnfd_name = nsd[0].get("nsd").get("vnfd-id")
        if isinstance(xnfd_name, list):
            xnfd_name = xnfd_name[0]
        response = requests.get("{}?id={}".format(
            self.url_xnfd_list, xnfd_name),
                                headers=self.headers,
                                verify=False)
        xnfd = response._content
        if xnfd is None:
            raise osm_exception.OSMPackageError(
                {"error": "Cannot retrieve suitable NF for NS package " +
                          "with name={}".format(xnfd_name),
                 "status": HttpCode.NOT_FOUND})
        xnfd = response.json()
        if isinstance(xnfd, list):
            xnfd = xnfd[0]
        xnfd_member_xnf = xnfd.get("id")

        # Iterate on all existing KDUs
        for xnfd_kdu in xnfd.get("kdu"):
            xnfd_kdu_name = xnfd_kdu.get("name")
            try:
                primitive_params = json.loads(primitive_params)
            except Exception:
                pass
            osm_payload = {
                "kdu_name": xnfd_kdu_name,
                "member_vnf_index": xnfd_member_xnf,
                "primitive": primitive_name,
                "primitive_params": primitive_params
            }
            resp = requests.post(
                instance_url,
                headers=self.headers,
                data=yaml_dump(osm_payload),
                verify=False)
            output = resp.json()
            action_id = output.get("id")
            status_code = output.get("status")
            if status_code is None:
                status_code = HttpCode.ACCEPTED
            if status_code >= 200 and status_code < 400:
                trigger_modes = ["action.{}".format(primitive_name)]
                event_msg = "SC with id={0} triggered action={1}".format(
                            nsi_id, primitive_name)
                LOGGER.info(event_msg)
                event_args = {
                   "xni-ip": xni_ip,
                }
                self.notify(
                    trigger_modes, event_msg, **event_args)
                success_msg = dict(ACTION_STATUS)
                success_msg["ns-id"] = nsi_id
                success_msg["ns-action-id"] = action_id
                success_msg["ns-action-name"] = primitive_name
                success_msg["ns-action-params"] = primitive_params
                success_msg["ns-action-status"] = "processing"
                success_msg["status"] = status_code
                return success_msg
            else:
                error_msg = {"status": status_code,
                             "error": output.get("detail")}
                return error_msg
