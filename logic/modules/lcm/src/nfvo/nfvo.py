#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2017-present i2CAT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
import time
from common.nfv.nfvo.osm.osm_r10 import OSMR10


class OSMR10(OSMR10):
    """
    OSM release 10 northbound API client (NBI)
    """

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    OSM = OSMR10()
    NSD_IDS = [x["_id"] for x in OSM.get_ns_descriptors()]
    print(random.choice(NSD_IDS))
    NSR = OSM.post_ns_instance("833bb02c-92e4-4fdb-ac55-cc927acfd2e7",
                               "Test",
                               "Test instance")
    print(OSM.get_ns_instance(NSR["id"]))
    time.sleep(180)
    OSM.delete_ns_instance(NSR["id"])
