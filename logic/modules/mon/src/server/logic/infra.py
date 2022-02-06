#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.infra.kubernetes import SOKubernetes
from common.utils.file_handling import FileHandling
from flask import make_response
import os
import yaml


class Infra(object):

    def __init__(self):
        self.config = FullConfParser()
        self.mon_category = self.config.get("infra.yaml")
        self.infra_category = self.mon_category.get("infrastructure")
        self.infrastructures = []
        for infra_name, infra_cfg in self.infra_category.items():
            infra_dict = {
                "name": infra_name,
            }
            infra_dict.update(infra_cfg)
        try:
            k8s_cfg_file = infra_cfg.get("config", {}).get("file", "")
            common_path = FileHandling.extract_common_path(
                os.path.abspath(__file__),
                os.path.normpath(k8s_cfg_file),
                "server")
#                "blueprints")
            k8s_cfg_file = os.path.normpath(
                            os.path.join(common_path, k8s_cfg_file))
            if os.path.isfile(k8s_cfg_file):
                k8s_cfg_ct = open(k8s_cfg_file, "r")
                kubeconfig_json = yaml.safe_load(k8s_cfg_ct)
                infra_dict.get("config", {})["data"] = kubeconfig_json
            self.infrastructures.append(infra_dict)
            self.k8s_client = SOKubernetes(
                infra_dict.get("config", {}).get("data"))
        except ConnectionRefusedError as e:
            return make_response(
                "Infrastructure with infra_name: {} may not be \
                    reachable. Details: {}"
                .format(infra_name, str(e)), 500)

    def infra_describe(self, infra_id: str) -> dict():
        # Parameters defined under /usr/local/lib/python3.8/
        # site-packages/kubernetes/client/api/core_v1_api.py
        try:
            infra_list = list(
                filter(lambda x: infra_id == x.get("id"),
                       self.infrastructures))
            if len(infra_list) != 1:
                raise Exception("Infrastructure does not exists in cfg infras")
        except Exception as e:
            return make_response(
                "Non-existing infra_id: {}. Details: {}"
                .format(infra_id, str(e)), 400)
        try:
            return self.k8s_client.nodes_describe(infra_id)
        except ConnectionRefusedError as e:
            return make_response(
                "Infrastructure with infra_id: {} may not be \
                    reachable. Details: {}"
                .format(infra_id, str(e)), 500)

    def infra_list(self, infra_id: str = None) -> list():
        result = []
        for infra in self.infrastructures:
            # Request for details on specific infra
            if infra_id is not None:
                if infra_id == infra.get("name"):
                    infra_id = infra.get("id")
                if infra_id == infra.get("id"):
                    result = self.infra_describe(infra_id)
                    return result
            # Request for details on all infras
            else:
                result.append(self.infra_describe(infra.get("id")))
        return result
