#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


from pydantic import BaseModel
from typing import List


class MonitoringInfraNodesList(BaseModel):
    name: str
    cpu: int
    ram: int
    disk: int


class MonitoringInfrastructure(BaseModel):
    id: str
    nodes: List[MonitoringInfraNodesList]
    tenant: str
    deployments: List[str]
