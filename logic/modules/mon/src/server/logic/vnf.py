#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import uuid


class VNF(object):

    @staticmethod
    def vnf_list() -> list():
        # TODO: dummy code. Also, models must be placed elsewhere,
        # common code should be grouped, clients should be called to
        # retrieve metrics, etc
        vnf_list = []
        metric_list = [
                "free -m -h | tail -2 | head -1 | tr -s " " | cut -d " " -f 4",
                "df -h",
                "ps aux | grep python"]
        metric_dict = {}
        for i, metric in enumerate(metric_list):
            metric_dict.update({
                "metric-name": "metric%d" % i,
                "metric-def": metric_list[i],
                "metric-value": "sample-value"
                })
        for vnf_i in range(0, 2):
            vnf_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "mon.vnf.%d" % vnf_i))
            vnf_list.append({
                "vnf-id": vnf_id,
                "metrics": metric_dict,
                })
        data = {"metrics": vnf_list}
        return data
