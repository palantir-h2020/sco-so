#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from fastapi import APIRouter
from common.server.http.http_code import HttpCode
from common.server.http.http_response_fastapi import HttpResponse


router = APIRouter()


@router.get("/")
def base():
    data = {"name": "api_api"}
    return HttpResponse.json(HttpCode.OK, data)
