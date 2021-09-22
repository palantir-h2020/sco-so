#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


def get_user_agent(request):
    ua_key = "HTTP_USER_AGENT"
    if ua_key in request.environ:
        return request.environ.get(ua_key)
    return ""
