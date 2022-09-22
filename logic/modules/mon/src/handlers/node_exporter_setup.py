#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from metrics.execute_command import ExecuteCommand


class NodeExporterSetup:
    """
    Installation of the node exporter on the xNF targets
    """

    def __init__(self) -> None:
        self.node_exporter_docker_cmd = (
            "sudo apt update && "
            + "sudo apt upgrade -y && "
            + "sudo apt-get remove docker docker-engine docker.io -y && "
            + "sudo apt install docker.io -y && "
            + "sudo snap install docker && "
            + "sudo docker pull prom/node-exporter && "
            + "sudo docker run --name prometheus-node-exporter -itd "
            + "-p 9100:9100 prom/node-exporter"
        )
        self.node_exporter_uninstall_cmd = (
            "sudo docker stop prometheus-node-exporter && "
            + "sudo docker rm prometheus-node-exporter && "
            + "sudo docker rmi prom/node-exporter && "
            + "sudo apt-get remove docker docker-engine docker.io -y"
        )
        pass

    def install_node_exporter(self, xnf_id):
        xnf_id = xnf_id
        xnf_ip = xnf_id.split(":")
        command = self.node_exporter_docker_cmd
        ExecuteCommand.execute_command(xnf_ip[0], command)

    def uninstall_node_exporter(self, xnf_id):
        xnf_id = xnf_id
        xnf_ip = xnf_id.split(":")
        command = self.node_exporter_uninstall_cmd
        ExecuteCommand.execute_command(xnf_ip[0], command)

    def manual_install_uninstall_exporter(self, request):
        request_body = request.json
        xnf_ip = request_body.get("xnf-ip")
        if request.method == "POST":
            if type(xnf_ip) == list:
                xnf_list_response = []
                for target in xnf_ip:
                    command = self.node_exporter_docker_cmd
                    xnf_response = ExecuteCommand.execute_command(
                            target, command)
                    xnf_list_response.append(xnf_response)
                response = {"Response": "Node Exporter Installation status on xNF(s) {}: {}"\
                       .format(xnf_ip, xnf_list_response)}
                return response
            else:
                response = {"Response": "xnf_ip must be a list"}
                return response
        if request.method == "DELETE":
            if type(xnf_ip) == list:
                xnf_list_response = []
                for target in xnf_ip:
                    command = self.node_exporter_uninstall_cmd
                    xnf_response = ExecuteCommand.execute_command(
                            target, command)
                    xnf_list_response.append(xnf_response)
                response = {"Response": "Node Exporter Uninstall status on xNF(s) {}: {}"\
                       .format(xnf_ip, xnf_list_response)}
                return response
            else:
                response = {"Response": "xnf_ip must be a list"}
                return response
