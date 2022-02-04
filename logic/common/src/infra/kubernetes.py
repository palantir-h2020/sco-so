#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")))
from common.exception.exception import SOException
from common.log.log import setup_custom_logger
from kubernetes import client as k8s_client, config as k8s_config
import math

LOGGER = setup_custom_logger(__name__)


class SOKubernetes():
    """
    Client for Kubernetes clusters.
    """

    def __init__(self, k8sconfig: str = None):
        self.cfg = k8s_config
        self.cfg.load_kube_config_from_dict(k8sconfig)
        self.k8s_api_v1 = k8s_client.CoreV1Api()

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

        def pod_describe(self, name: str, namespace: str = None) -> dict():
            if namespace is not None:
                return self.k8s_api_v1.read_namespaced_pod(namespace, name)
            pod_dict = {}
            pod_list = self.k8s_api_v1.list_pod_for_all_namespaces(watch=False)
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
