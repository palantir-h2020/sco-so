#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.utils.file_handling import FileHandling
# from common.server.http.http_code import HttpCode
# from handlers.prometheus_targets_handler import PrometheusTargetsHandler
# from flask import make_response
# import os
from kubernetes import client as k8s_client, config as k8s_config
import math
import os
import pprint
import uuid
import yaml


class VIM(object):

    def __init__(self):
        self.config = FullConfParser()
        self.mon_category = self.config.get("mon.yaml")
        self.infra_category = self.mon_category.get("infrastructure")
        # print("self.infra_category = " + str(self.infra_category))
        self.infrastructures = []
        for infra_name, infra_cfg in self.infra_category.items():
            infra_dict = {
                "name": infra_name,
            }
            infra_dict.update(infra_cfg)
            self.infrastructures.append(infra_dict)
            k8s_cfg_file = infra_cfg.get("config", {}).get("file", "")
            # print("file -> " + str(k8s_cfg_file))
            # print("file (normpath) -> " + str(os.path.normpath(k8s_cfg_file)))
            common_path = FileHandling.extract_common_path(
                os.path.abspath(__file__),
                os.path.normpath(k8s_cfg_file),
                "server")
            k8s_cfg_file = os.path.normpath(
                            os.path.join(common_path, k8s_cfg_file))
            if os.path.isfile(k8s_cfg_file):
                k8s_cfg_ct = open(k8s_cfg_file, "r")
                kubeconfig_json = yaml.safe_load(k8s_cfg_ct)
                # print(kubeconfig_json)
                k8s_config.load_kube_config_from_dict(kubeconfig_json)
            # REMOVE
            print("infra: " + str(infra_cfg))

    def vim_list(self) -> list():
        # TODO: dummy code. Also, models must be placed elsewhere,
        # common code should be grouped, clients should be called to
        # retrieve metrics, etc
        k8s_api_h = k8s_client.CoreV1Api()
        # print("Listing pods with their IPs:")
        # ret = k8s_api_h.list_pod_for_all_namespaces(watch=False)
        # print(ret)
        # Parameters defined under /usr/local/lib/python3.8/
        # site-packages/kubernetes/client/api/core_v1_api.py
        ret = k8s_api_h.list_node_with_http_info(
            watch=False, timeout_seconds=3, _request_timeout=1)
        # CHANGE TO WHAT IS DEFINED IN OSM? OR IN SCO/SO?
        tmp_uuid = str(uuid.uuid4())
        res = {
                "id": tmp_uuid,
                "nodes": [],
                "tenant": "sample",
                "deployments": ["cloud"],
                }
        for r in ret[0].items:
            node_addresses = r._status.addresses
            node_name = list(filter(
                lambda x: x.type == "Hostname",
                node_addresses))[0].address
            node_cpu = int(r._status.allocatable.get("cpu"))
            # This was in bytes
            node_ram = r._status.allocatable.get("memory")
            node_ram = int(node_ram.replace("Ki", ""))
            node_ram = math.floor(node_ram / 1000)
            # This is in kbytes and included the units
            node_disk = r._status.allocatable.get("ephemeral-storage")
            node_disk = int(node_disk.replace("Ki", ""))
            node_disk = math.floor(node_disk / (1000*1000))
            node_dict = {
                "name": node_name,
                "cpu": node_cpu,
                "ram": node_ram,
                "disk": node_disk,
                }
            if node_dict is not None:
                res["nodes"].append(node_dict)
            # print("Node name={}, CPU={}, RAM={}, Disk={}".format(
            #     node_name,
            #     r._status.allocatable.get("cpu"),
            #     r._status.allocatable.get("memory"),
            #     r._status.allocatable.get("ephemeral-storage")))
        pprint.pprint(res)
        return res

#        vim_list = []
#        metric_list = [
#                "free -m -h",
#                "df -h",
#                "netstat -apen"]
#        metric_dict = {}
#        for i, metric in enumerate(metric_list):
#            metric_dict.update({
#                "metric-name": "metric%d" % i,
#                "metric-def": metric_list[i],
#                "metric-value": "sample-value"
#                })
#        for vim_i in range(0, 2):
#            vim_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "mon.vim.%d" % vim_i))
#            vim_list.append({
#                "vim-id": vim_id,
#                "metrics": metric_dict,
#                })
#        data = {"metrics": vim_list}
#        return data
