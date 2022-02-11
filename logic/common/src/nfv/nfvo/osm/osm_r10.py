#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.nfv.nfvo.osm.osm import OSM


class OSMR10(OSM):
    """
    OSM release 10 northbound API client (NBI).
    """

    def __init__(self):
        super().__init__()
