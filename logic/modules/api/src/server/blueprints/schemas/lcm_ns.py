#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from fastapi import Query
from pydantic import BaseModel
from typing import List, Optional


class NSInstanceAction(BaseModel):
    action_name: str = None
    action_params: Optional[dict] = Query(None)


class NSInstanceDeployment(BaseModel):
    action_name: Optional[str] = None
    action_params: Optional[dict] = Query(None)
    description: Optional[str] = None
    name: Optional[str] = None
    ssh_key: Optional[List[str]] = None
    vim_id: Optional[str] = None
