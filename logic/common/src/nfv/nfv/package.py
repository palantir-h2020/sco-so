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
from common.nfv.nfvo.osm.osm_r10 import OSMR10
from common.nfv.nfvo.osm.osm import OSMException, OSMPackageConflict,\
     OSMPackageError, OSMUnknownPackageType, OSMPackageNotFound
from common.server.http import content
from common.server.mocks.package import MockPackage as package_m


class NFVPackageConflict(Exception):
    pass


class NFVPackageError(Exception):
    pass


class NFVUnknownPackageType(Exception):
    pass


class NFVPackageNotFound(Exception):
    pass


def get_osm_instance(release: int):
    try:
        orchestrator = globals().get("OSMR{}".format(release), None)
        if callable(orchestrator):
            orchestrator = orchestrator()
        else:
            orchestrator = OSMR10()
        return orchestrator
    except Exception:
        raise SOException(
            "Cannot create instance of OSMR{}".format(release))


@content.on_mock(package_m().onboard_package_mock)
def onboard_package(pkg_path, release=None):
    """
    Uploads a locally stored xNF or NS package to the NFVO.
    Calling this method and POSTing a file from a remote server will
    result into more time to transfer the package.

    @param pkg_path Local binary file
    @return output Structure with provided path and transaction ID
    """
    orchestrator = get_osm_instance()
    try:
        return orchestrator.onboard_package(pkg_path)
    except OSMPackageConflict:
        raise NFVPackageConflict
    except OSMUnknownPackageType:
        raise NFVUnknownPackageType
    except OSMPackageError:
        raise NFVPackageError


@content.on_mock(package_m().onboard_package_remote_mock)
def onboard_package_remote(pkg_path, release=None):
    """
    Uploads a remotely stored xNF or NS package to the NFVO.

    @param pkg_path Remote path to the package
    @return output Structure with provided path and transaction ID
    """
    orchestrator = get_osm_instance()
    try:
        return orchestrator.onboard_package_remote(pkg_path)
    except OSMPackageNotFound:
        raise NFVPackageNotFound
    except OSMPackageConflict:
        raise NFVPackageConflict
    except OSMUnknownPackageType:
        raise NFVUnknownPackageType
    except OSMPackageError:
        raise NFVPackageError


@content.on_mock(package_m().remove_package_mock)
def remove_package(pkg_name, release=None):
    orchestrator = get_osm_instance()
    try:
        return orchestrator.remove_package(pkg_name)
    except OSMUnknownPackageType:
        raise NFVUnknownPackageType
    except OSMPackageNotFound:
        raise NFVPackageNotFound
    except OSMPackageConflict:
        raise NFVPackageConflict
    except OSMException:
        raise OSMException
