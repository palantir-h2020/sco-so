#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.nfv.nfvo.osm.osm import OSM
# from common.nfv.nfvo.osm.osm import check_authorization, OSM
# import json
# import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OSMR10(OSM):
    """
    OSM release 10 northbound API client (NBI).
    """

    def __init__(self):
        super().__init__()

    # @check_authorization
    # def get_ns_descriptors(self, ns_name=None):
    #     """
    #     Sample of an overriding method.
    #     """
    #     response = requests.get(self.ns_descriptors_url,
    #                             headers=self.headers,
    #                             verify=False)
    #     nsds = json.loads(response.text)
    #     if ns_name:
    #         return {"ns": [x for x in nsds
    #                        if x["name"] == ns_name]}
    #     return {"ns": [x for x in nsds]}
