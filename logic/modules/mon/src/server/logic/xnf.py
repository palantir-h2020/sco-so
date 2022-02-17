#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import uuid


class XNF(object):

    @staticmethod
    def xnf_list() -> list():
        # TODO: dummy code. Also, models must be placed elsewhere,
        # common code should be grouped, clients should be called to
        # retrieve metrics, etc
        xnf_list = []
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
        for xnf_i in range(0, 2):
            xnf_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "mon.xnf.%d" % xnf_i))
            xnf_list.append({
                "xnf-id": xnf_id,
                "metrics": metric_dict,
                })
        data = {"metrics": xnf_list}
        return data
