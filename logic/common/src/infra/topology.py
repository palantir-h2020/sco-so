#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")))
from common.log.log import setup_custom_logger
# from ruamel import yaml
import json
import requests
import yaml

LOGGER = setup_custom_logger(__name__)


class NetworkLandscape:
    """
    Handles the network topology or landscape.
    This is specially useful for the remediation subcomponents,
    which need to understand where exactly a security capability/mechanism
    is deployed.
    """

    @staticmethod
    def topology_creation(tenant: str, topology_str: str):
        """
        Ingests a YAML file and stores it internally.
        """
        print(topology_str)
        topology_yaml = yaml.safe_load(topology_str)
        print(topology_yaml)
        print("bbb")
        topology_json = json.dumps(topology_yaml)
        print(topology_json)
        # TODO perform any operation and persist into the DB
        # TODO review returned structure and HTTP code
        topology_stored = {
            "tenant": tenant,
            "topology": topology_json,
        }
        print(topology_stored)
        print("ccc")
        return topology_stored

    @staticmethod
    def topology_retrieval(tenant: str = None):
        # TODO
        # TODO RETURN YAML BY DEFAULT
        # TODO RETURN HTTP 503 IF NOTHING WAS PREVIOUSLY DEFINED
        # TODO RETRIEVE "TYPE"/"NATURE" FROM SM
        """
        Retrieves the network topology from the information
        stored in the DB and complements it with data in memory,
        such as the runtime data for the SCs.
        """
        topology_json = {
            "DeploymentNode": {
                "microk8s": {
                    "vim_id": "1ce8afba-635c-4e3c-b6d1-01207e1b3f67",
                    "network_interfaces": {
                        "ens18": {
                            "internet_gw": True,
                            "ipv4_address": "10.101.41.141"}
                        }
                },
                "polito": {
                    "vim_id": "6663bb03-5fc1-47fe-8628-f8b80c53faf6",
                    "network_interfaces": {
                        "eno3": {
                            "internet_gw": True,
                            "ipv4_address": "10.101.44.1"}
                        }
                    },
                },
            "Links": [
                "DeploymentNode.polito.eno3,ProtectedHosts.h1.h1-eth0",
                ],
            "ProtectedHosts": {
                "h1": {
                    "default_interface": "h1-eth0",
                    "network_interfaces": {
                        "h1-eth0": {
                            "ipv4_address": "10.0.0.2"}
                        }
                    },
                "h2": {
                    "default_interface": "h2-eth0",
                    "network_interfaces": {
                        "h2-eth0": {
                            "ipv4_address": "10.0.0.4"}
                        }
                    },
                "h3": {
                    "default_interface": "h3-eth0",
                    "network_interfaces": {
                        "h3-eth0": {
                            "ipv4_address": "10.0.0.6"},
                        "h3-eth1": {
                            "ipv4_address": "10.0.0.7"}
                        }
                    }
                },
            "Switches": {}
        }
        # Fill in dynamically with runtime data on SCs
        # FIXME use envvars and others
        url_ns_list = "http://10.101.41.168:50101/lcm/ns"
        headers = {"Accept": "application/json"}
        response = requests.get(url_ns_list,
                                headers=headers,
                                verify=False)
        running_nss = json.loads(response.text)
        for deployment_node in topology_json.get("DeploymentNode").items():
            # deployment_node_name = deployment_node[0]
            # Get contents
            deployment_node = deployment_node[1]
            vim_id = deployment_node.get("vim_id")
            sc_dict = {
                "security_capabilities": {}
            }
            for ns in running_nss.get("ns"):
                if vim_id == ns.get("vim").get("id"):
                    # TODO Fill in the "type" data using the tests in
                    # logic/common/src/events/kafka to query the SM
                    sc_info = {
                        ns.get("name"): {
                            "id": ns.get("id"),
                            "package-name": ns.get("package").get("name"),
                            "type": "<type_from_sm>",
                        }
                    }
                    sc_dict.get("security_capabilities").update(sc_info)
            deployment_node.update(sc_dict)
        # TODO: no explicit tenant? Return the full list of them
        if tenant is None:
            topology_retrieved = {
                "topologies": [
                    {
                        "tenant": "tenant1",
                        "topology": topology_json,
                    },
                    {
                        "tenant": "tenant2",
                        "topology": {},
                    },
                ]
            }
        else:
            topology_retrieved = {
                "tenant": tenant,
                "topology": topology_json,
            }
            # FIXME: remove, this is a test just to illustrate the 503 error
            if tenant == "force-error":
                topology_retrieved["topology"] = {}
        return topology_retrieved
