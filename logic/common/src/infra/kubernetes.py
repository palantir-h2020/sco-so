#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")))
from common.exception.exception import SOException, SOConfigException
from common.log.log import setup_custom_logger
from common.utils.file_handling import FileHandling
from kubernetes import client as k8s_client, config as k8s_config
from kubernetes.config.config_exception import ConfigException as\
    K8sConfigException
import math
import yaml

LOGGER = setup_custom_logger(__name__)


class SOKubernetes():
    """
    Client for Kubernetes clusters.
    """

    def __init__(self, k8sconfig_path: str):
        self.cfg = k8s_config
        self._load_kubeconfig(k8sconfig_path)
        self.k8s_api_v1 = k8s_client.CoreV1Api()

    def _load_kubeconfig(self, k8sconfig_path: str):
        common_path = FileHandling.extract_common_path(
            os.path.abspath(__file__),
            os.path.normpath(k8sconfig_path),
            "infra")
        k8s_cfg_file = os.path.normpath(
                       os.path.join(common_path, k8sconfig_path))
        self.kubeconfig = None
        if os.path.isfile(k8s_cfg_file):
            k8s_cfg_ct = open(k8s_cfg_file, "r")
            self.kubeconfig = yaml.safe_load(k8s_cfg_ct)
        try:
            self.cfg.load_kube_config_from_dict(self.kubeconfig)
        except K8sConfigException:
            raise SOConfigException("Missing file: {}".format(k8s_cfg_file))

    def nodes_describe(self, infra_id: str) -> dict():
        # Parameters defined under /usr/local/lib/python3.8/
        # site-packages/kubernetes/client/api/core_v1_api.py
        result = {}
        infra_dict = {}
        try:
            ret = self.k8s_api_v1.list_node_with_http_info(
                watch=False, timeout_seconds=3, _request_timeout=2)
        except ConnectionRefusedError:
            SOException.internal_error(
                "Infrastructure with infra_id: " +
                "{} may not be reachable. Details: {}")
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
        return result

    def namespace_list(self, namespace_id: str = None) -> list:
        namespaces = [x.metadata.name for x in self.k8s_api_v1.list_namespace(
                watch=False, timeout_seconds=3, _request_timeout=2).items]
        if namespace_id is not None:
            # Note: this is particular to the way OSM creates the namespaces:
            # e.g.: "squid-metrics-kdu-8770df0a-380d-4cf9-ae40-ee698172b9bd"
            # and therefore, filtering must not be necessarily explicit
            namespaces = list(
                    filter(lambda x: x == namespace_id or
                           x.endswith("-{}".format(namespace_id)), namespaces))
        return namespaces

    def pod_list(self, namespace_id: str = None) -> list:
        pod_list_ns = []
        namespaces = self.namespace_list(namespace_id)
        for namespace in namespaces:
            pods = self.k8s_api_v1.list_namespaced_pod(
                namespace=namespace, watch=False, timeout_seconds=3,
                _request_timeout=2)
            pod_ns_struct = {
                "namespace": namespace,
                "pods": pods
            }
            pod_list_ns.append(pod_ns_struct)
        return pod_list_ns

    def pod_describe(self, name: str, namespace: str = None) -> dict():
        if namespace is not None:
            return self.k8s_api_v1.read_namespaced_pod(namespace, name)
        pod_dict = {}
        pod_list = self.pod_list(namespace)
        for pod in pod_list.items:
            curr_name = pod.metadata.name
            if name == curr_name:
                namespace = pod.metadata.namespace
                nodes = list(map(
                    lambda x: x.name, pod.metadata.owner_references))
                container_id = list(map(
                    lambda x: x.container_id,
                    pod.status._container_statuses))
                image_id = list(map(
                    lambda x: x.image_id, pod.status._container_statuses))
                pod_dict = {
                    "name": curr_name,
                    "namespace": namespace,
                    "nodes": nodes,
                    "container-id": container_id,
                    "image-id": image_id,
                }
        return pod_dict
