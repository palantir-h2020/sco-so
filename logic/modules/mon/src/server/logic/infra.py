#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.exception.exception import SOConfigException,\
    SONetworkConnectionException, SONotFoundException
from common.infra.kubernetes import SOKubernetes
from common.server.http.http_code import HttpCode
from uuid import UUID


class Infra(object):

    def __init__(self):
        self.config = FullConfParser()
        self.mon_category = self.config.get("infra.yaml")
        self.infra_category = self.mon_category.get("infrastructure")
        self.infrastructures = []
        self.k8s_clients = {}
        infra_dict = {}
        for infra_name, infra_cfg in self.infra_category.items():
            infra_id = infra_cfg.get("id")
            infra_dict = {
                "name": infra_name,
            }
            infra_dict.update(infra_cfg)
            try:
                k8s_cfg_file = infra_cfg.get("config", {}).get("file", "")
                self.k8s_clients[infra_id] = SOKubernetes(k8s_cfg_file)
                infra_dict.get("config", {})["data"] = \
                    self.k8s_clients[infra_id].kubeconfig
                self.infrastructures.append(infra_dict)
            except ConnectionRefusedError as e:
                raise SONetworkConnectionException(
                     {"error": "Infrastructure with infra_id: {} may not be \
                        reachable. Details: {}".format(infra_id, str(e)),
                      "status": HttpCode.NET_CONN_TIMEOUT})

    def infra_describe(self, infra_id: str) -> dict():
        # Parameters defined under /usr/local/lib/python3.8/
        # site-packages/kubernetes/client/api/core_v1_api.py
        try:
            infra_list = list(
                filter(lambda x: infra_id == x.get("id"),
                       self.infrastructures))
            if len(infra_list) != 1:
                raise SOConfigException(
                        {"error": "Infrastructure {} not defined in cfg file"
                            .format(infra_id),
                            "status": HttpCode.IMPROPER_USAGE})
        except Exception as e:
            raise SONotFoundException(
                    {"error": "Non-existing infra_id: {}. Details: {}"
                        .format(infra_id, str(e)),
                        "status": HttpCode.NOT_FOUND})
        try:
            return self.k8s_clients[infra_id].nodes_describe(infra_id)
        except KeyError:
            raise SOConfigException(
                    {"error": "Infrastructure {}".format(infra_id) +
                              "not properly defined or initialised",
                        "status": HttpCode.IMPROPER_USAGE})
        except ConnectionRefusedError as e:
            raise SONetworkConnectionException(
                {"error": "Infrastructure with infra_id: {} may not be \
                    reachable. Details: {}".format(infra_id, str(e)),
                    "status": HttpCode.NET_CONN_TIMEOUT})

    # Called externally
    def infra_list(self, infra_id: str = None) -> list():
        result = {"infrastructures": []}
        infra_res = {}
        for infra in self.infrastructures:
            if infra_id is not None:
                if infra_id == infra.get("id"):
                    infra_res = self.infra_describe(infra_id)
                else:
                    continue
            # Request for details on all infras
            else:
                infra_res = self.infra_describe(infra.get("id"))
            if infra_res is not None and len(infra_res) > 0:
                infra_res.update(
                    {k: infra.get(k) for k in
                        ["deployments", "id", "name", "tenant", "type"]
                     })
                result.get("infrastructures").append(infra_res)
            infra_res = {}
        if len(result.get("infrastructures")) == 0:
            raise SONotFoundException(
                 {"error": "Non-existing infrastructure for " +
                           "id: {}".format(infra_id),
                  "status": HttpCode.NOT_FOUND})
        return result

    # Called externally
    def service_list(self, infra_id: str, ns_id: str = None) -> list():
        service_struct = {"ns": [], "infra-id": infra_id}
        namespace_id = None
        if ns_id is not None:
            try:
                UUID(ns_id)
            except Exception:
                raise SONotFoundException(
                     {"error": "Non-existing service (id: " +
                         "{}) for infrastructure with id: {}"
                               .format(ns_id, infra_id),
                      "status": HttpCode.NOT_FOUND})
            namespace_id = "-".join(ns_id.split("-")[-5:])
        try:
            namespaces = self.k8s_clients[infra_id].namespace_list(
                    namespace_id)
        except KeyError:
            raise SOConfigException(
                    {"error": "Infrastructure {}".format(infra_id) +
                              "not properly defined or initialised",
                        "status": HttpCode.IMPROPER_USAGE})
        pods_filter_ns = []
        pods_filter_pod = []
        namespaces_filter = []
        # If no service -id is provided, all feasible namespaces will be used
        if ns_id is None:
            for namespace in namespaces:
                ns_id_valid = "-".join(namespace.split("-")[-5:])
                try:
                    UUID(ns_id_valid)
                    namespaces_filter.append(namespace)
                except Exception:
                    # If not a namespace for a NS, ignore this iteration
                    pass
        # Otherwise use the previously computed namespace
        else:
            namespaces_filter = namespaces

        if len(namespaces_filter) == 0:
            raise SONotFoundException(
                 {"error": "Non-existing service (id: " +
                     "{}) for infrastructure with id: {}"
                           .format(ns_id, infra_id),
                  "status": HttpCode.NOT_FOUND})
        for namespace in namespaces_filter:
            try:
                pods = self.k8s_clients[infra_id].pod_list(namespace)
            except KeyError:
                raise SOConfigException(
                        {"error": "Infrastructure {}".format(infra_id) +
                                  "not properly defined or initialised",
                            "status": HttpCode.IMPROPER_USAGE})
            for pod_iter in pods:
                pod_iter_namespace = pod_iter.get("namespace")
                if namespace == pod_iter_namespace:
                    pod_iter_pods = pod_iter.get("pods")
                    pods_filter_ns.append(pod_iter_pods)
            for pods_filter_ns_items in pods_filter_ns:
                for pods_filter_ns_item in pods_filter_ns_items.items:
                    if not pods_filter_ns_item.metadata.name.startswith(
                            "modeloperator") and "-operator-" not in\
                                    pods_filter_ns_item.metadata.name:
                        pods_filter_pod.append(pods_filter_ns_item)
            ns_desc = {"namespace": namespace, "pods": [],
                       "ns-id": "-".join(namespace.split("-")[-5:])}
            pod_desc = {}
            image_ids = []
            container_ids = []
            for pod in pods_filter_pod:
                if len(image_ids) == 0:
                    image_ids = [st.image_id for st in
                                 pod.status.container_statuses]
                if len(container_ids) == 0:
                    container_ids = [st.container_id for st in
                                     pod.status.container_statuses]
                pod_desc = {"name": pod.metadata.name, "ip": pod.status.pod_ip,
                            "node-ip": pod.status.host_ip, "containers": []}
                pod_cont_desc = {}
                if len(image_ids) == len(container_ids) \
                        and len(container_ids) > 0:
                    container_id = container_ids[0]
                    image_id = image_ids[0]
                    pod_cont_desc.update({"container-id": container_id,
                                          "image-id": image_id})
                    try:
                        container_ids = container_ids[1:]
                        image_ids = image_ids[1:]
                    except Exception:
                        pass
                pod_desc.get("containers").append(pod_cont_desc)
            ns_desc.get("pods").append(pod_desc)
            service_struct.get("ns").append(ns_desc)
        return service_struct
