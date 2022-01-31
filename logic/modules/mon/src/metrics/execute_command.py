#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import os
import paramiko
import time

from common.config.parser.fullparser import FullConfParser


class ExecuteCommand:
    """
    Paramiko SSH connection to execute command on remote VNF.
    """

    def execute_command(vnf_ip, command) -> str:
        parser = FullConfParser()
        mon = parser.get("mon.yaml")
        prom = mon.get("prometheus")
        user_name = prom.get("user-name")
        vnf_ip = vnf_ip
        key_filename = os.path.abspath("../data/key/target-mon")
        command = command

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(vnf_ip, username=user_name, key_filename=key_filename)
            STDIN, STDOUT, STDERR = client.exec_command(command)
            time.sleep(1)
            COMMAND_RESPONSE = STDOUT.read().decode()
            client.close()
            return COMMAND_RESPONSE
        except:
            return "{} is unreachable. Please verify the connection, otherwise check target-mon key".format(
                vnf_ip
            )
