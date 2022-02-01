#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint, request
from server.logic.vim import VIM

so_blueprints = Blueprint("so__mon__vim", __name__)
vim_handler = VIM()


@so_blueprints.route("/mon/vim", methods=["GET"])
def vim_list() -> HttpResponse:
    vim_id = request.args.get("vim-id")
    vim_name = request.args.get("vim-name")
    filter_vim = vim_id
    if vim_id is None:
        filter_vim = vim_name
    data = vim_handler.vim_list(filter_vim)
    return HttpResponse.formatted(data, HttpCode.OK)
