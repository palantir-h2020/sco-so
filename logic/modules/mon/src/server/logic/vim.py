#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.utils.file_handling import FileHandling
# from flask import jsonify
from flask import make_response
from kubernetes import client as k8s_client, config as k8s_config
import math
import os
import yaml


class VIM(object):

    def __init__(self):
        self.config = FullConfParser()
        self.mon_category = self.config.get("mon.yaml")
        self.infra_category = self.mon_category.get("infrastructure")
        self.infrastructures = []
        for infra_name, infra_cfg in self.infra_category.items():
            infra_dict = {
                "name": infra_name,
            }
            infra_dict.update(infra_cfg)
            k8s_cfg_file = infra_cfg.get("config", {}).get("file", "")
            common_path = FileHandling.extract_common_path(
                os.path.abspath(__file__),
                os.path.normpath(k8s_cfg_file),
                "server")
            k8s_cfg_file = os.path.normpath(
                            os.path.join(common_path, k8s_cfg_file))
            if os.path.isfile(k8s_cfg_file):
                k8s_cfg_ct = open(k8s_cfg_file, "r")
                kubeconfig_json = yaml.safe_load(k8s_cfg_ct)
                infra_dict.get("config", {})["data"] = kubeconfig_json
            self.infrastructures.append(infra_dict)

    def vim_describe(self, vim_id: str) -> dict():
        # Parameters defined under /usr/local/lib/python3.8/
        # site-packages/kubernetes/client/api/core_v1_api.py
        result = {}
        infra_dict = {}
        try:
            infra_list = list(
                filter(lambda x: vim_id == x.get("id"),
                       self.infrastructures))
            if len(infra_list) != 1:
                raise Exception("Infrastructure does not exists in cfg infras")
            infra_dict = infra_list[0]
        except Exception as e:
            return make_response(
                "Non-existing vim_id: {}. Details: {}"
                .format(vim_id, str(e)), 400)
        try:
            k8s_config.load_kube_config_from_dict(
                infra_dict.get("config", {}).get("data", {}))
            self.k8s_api_v1 = k8s_client.CoreV1Api()
            ret = self.k8s_api_v1.list_node_with_http_info(
                watch=False, timeout_seconds=3, _request_timeout=2)
        except ConnectionRefusedError as e:
            return make_response(
                "Infrastructure with vim_id: {} may not be \
                    reachable. Details: {}"
                .format(vim_id, str(e)), 500)
            return result
        result.update({
                "id": infra_dict.get("id"),
                "nodes": [],
                "tenant": infra_dict.get("tenant"),
                "deployments": infra_dict.get("deployments"),
                })
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
                result.get("nodes").append(node_dict)
        # return jsonify(result)
        return result

    def vim_list(self, vim_id: str = None) -> list():
        result = []
        for infra in self.infrastructures:
            # Request for details on specific infra
            if vim_id is not None:
                if vim_id == infra.get("name"):
                    vim_id = infra.get("id")
                if vim_id == infra.get("id"):
                    result = self.vim_describe(vim_id)
                    return result
            # Request for details on all infras
            else:
                result.append(self.vim_describe(infra.get("id")))
        return result
