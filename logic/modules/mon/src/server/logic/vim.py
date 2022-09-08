#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import uuid


class VIM(object):

    @staticmethod
    def vim_list() -> list():
        # TODO: dummy code. Also, models must be placed elsewhere,
        # common code should be grouped, clients should be called to
        # retrieve metrics, etc
        vim_list = []
        metric_list = [
                "free -m -h",
                "df -h",
                "netstat -apen"]
        metric_dict = {}
        for i, metric in enumerate(metric_list):
            metric_dict.update({
                "metric-name": "metric%d" % i,
                "metric-def": metric_list[i],
                "metric-value": "sample-value"
                })
        for vim_i in range(0, 2):
            vim_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "mon.vim.%d" % vim_i))
            vim_list.append({
                "vim-id": vim_id,
                "metrics": metric_dict,
                })
        data = {"metrics": vim_list}
        return data
