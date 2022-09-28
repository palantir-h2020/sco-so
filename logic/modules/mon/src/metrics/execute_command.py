#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.config.parser.fullparser import FullConfParser
import os
import paramiko
import time


class ExecuteCommand:
    """
    Paramiko SSH connection to execute command on remote xNF.
    """

    def execute_command(xnf_ip, command) -> str:
        parser = FullConfParser()
        cfg_mon = parser.get("mon.yaml")
        cfg_mon_prom = cfg_mon.get("prometheus")
        cfg_mon_user_name = cfg_mon_prom.get("user-name")
        xnf_ip = xnf_ip
        cfg_so = parser.get("so.yaml")
        cfg_so_xnfs = cfg_so.get("xnfs")
        cfg_ssh = cfg_so_xnfs.get("general", {}).get("ssh-key")
        key_filename = "keys/{}".format(cfg_ssh)
        command = command

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(xnf_ip, username=cfg_mon_user_name,
                           key_filename=key_filename)
            STDIN, STDOUT, STDERR = client.exec_command(command)
            time.sleep(1)
            COMMAND_RESPONSE = STDOUT.read().decode()
            client.close()
            return COMMAND_RESPONSE
        except Exception:
            err_message = "{} is unreachable. {} {}".format(
                    xnf_ip,
                    "Please verify the connection, otherwise",
                    "check \"network_function\" key")
            err = {"Error": err_message}
            return err
