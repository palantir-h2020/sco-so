#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from metrics.execute_command import ExecuteCommand


class NodeExporterSetup:
    """
    Installation of the node exporter on the VNF targets
    """

    def __init__(self) -> None:
        self.node_exporter_docker_cmd = (
            "sudo docker pull prom/node-exporter && "
            + "sudo docker run --name prometheus-node-exporter -itd "
            + "-p 9100:9100 prom/node-exporter"
        )
        self.node_exporter_uninstall_cmd = (
            "sudo docker stop prometheus-node-exporter && "
            + "sudo docker rm prometheus-node-exporter && "
            + "sudo docker rmi prom/node-exporter"
        )
        pass

    def install_node_exporter(self, vnf_id):
        vnf_id = vnf_id
        vnf_ip = vnf_id.split(":")
        command = self.node_exporter_docker_cmd
        ExecuteCommand.execute_command(vnf_ip[0], command)

    def uninstall_node_exporter(self, vnf_id):
        vnf_id = vnf_id
        vnf_ip = vnf_id.split(":")
        command = self.node_exporter_uninstall_cmd
        ExecuteCommand.execute_command(vnf_ip[0], command)

    def manual_install_uninstall_exporter(self, request):
        request_body = request.json
        vnf_ip = request_body.get("vnf-ip")
        if request.method == "POST":
            if type(vnf_ip) == list:
                vnf_list_response = []
                for target in vnf_ip:
                    command = self.node_exporter_docker_cmd
                    vnf_response = ExecuteCommand.execute_command(
                            target, command)
                    vnf_list_response.append(vnf_response)
                return "Node Exporter Installation status on VNF(s) {}: {}"\
                       .format(vnf_ip, vnf_list_response)
            else:
                return "vnf_ip must be a list"
        if request.method == "DELETE":
            if type(vnf_ip) == list:
                vnf_list_response = []
                for target in vnf_ip:
                    command = self.node_exporter_uninstall_cmd
                    vnf_response = ExecuteCommand.execute_command(
                            target, command)
                    vnf_list_response.append(vnf_response)
                return "Node Exporter Uninstall status on VNF(s) {}: {}"\
                       .format(vnf_ip, vnf_list_response)
            else:
                return "vnf_ip must be a list"
