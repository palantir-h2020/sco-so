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

from common.exception.exception import SOException
from common.nfv import package as pkg
from common.nfv.package import NFVPackageConflict
from common.nfv.package import NFVPackageError
from common.nfv.package import NFVUnknownPackageType
from common.nfv.package import NFVPackageNotFound
from common.so.osm.osm import OSMException
from common.server.http import content
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from common.nfv.nfvo.osm.endpoints import NfvoEndpoints as endpoints
from flask import Blueprint
from flask import request

so_views = Blueprint("so_pkg_views", __name__)


@so_views.route(endpoints.PKG_ONBOARD, methods=["POST"])
@content.expect_json_content
def onboard_package():
    exp_ct = "multipart/form-data"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    form_param = "package"
    if not(len(request.files) > 0 and form_param in request.files.keys()):
        SOException.improper_usage("Missing file")
    pkg_bin = request.files.get(form_param)
    try:
        response = HttpResponse.json(HttpCode.ACCEPTED,
                                     pkg.onboard_package(pkg_bin, 4))
    except NFVPackageConflict:
        msg = "Package already onboarded and/or missing dependencies"
        SOException.improper_usage(msg)
    except NFVUnknownPackageType:
        msg = "Could not guess package type"
        SOException.improper_usage(msg)
    except NFVPackageError:
        msg = "OSMR4 package reading error"
        SOException.improper_usage(msg)
    return response


@so_views.route(endpoints.PKG_ONBOARD_REMOTE, methods=["POST"])
@content.expect_json_content
def onboard_package_remote():
    exp_ct = "application/json"
    if exp_ct not in request.headers.get("Content-Type", ""):
        SOException.invalid_content_type("Expected: {}".format(exp_ct))
    if not content.data_in_request(request, ["path"]):
        SOException.improper_usage("Missing argument: path")
    file_path = request.json.get("path")
    try:
        response = HttpResponse.json(HttpCode.ACCEPTED,
                                     pkg.onboard_package_remote(file_path, 4))
    except NFVPackageConflict:
        msg = "Package already onboarded and/or missing dependencies"
        SOException.improper_usage(msg)
    except NFVUnknownPackageType:
        msg = "Could not guess package type"
        SOException.improper_usage(msg)
    except NFVPackageError:
        msg = "OSMR4 package reading error"
        SOException.improper_usage(msg)
    except NFVPackageNotFound:
        msg = "OSM Package not found"
        SOException.improper_usage(msg)
    return response


@so_views.route(endpoints.PKG_REMOVE, methods=["DELETE"])
def remove_package(vnsf_name):
    try:
        return HttpResponse.json(HttpCode.ACCEPTED,
                                 pkg.remove_package(vnsf_name, 4))
    except NFVPackageNotFound:
        SOException.improper_usage("Package not found")
    except NFVUnknownPackageType:
        SOException.improper_usage("Unknown package type")
    except NFVPackageConflict:
        SOException.improper_usage("Conflict removing package")
    except OSMException:
        SOException.improper_usage("OSM Exception")
