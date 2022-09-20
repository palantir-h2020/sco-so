#!/bin/bash

# Copyright 2021-present i2CAT
#
# Licensed under ???


# Undeployment
if [[ -f ${docker_compose} ]]; then
    docker-compose -p ${SO_MODL_NAME} ps
    docker-compose -p ${SO_MODL_NAME} down
fi

# Remove utils-related dependencies and sources
mkdir -p ${PWD}/reqs/utils
rm -rf ${PWD}/uti

# Remove module-related dependencies, sources and configuration
mkdir -p ${PWD}/reqs/local
rm -rf ${PWD}/src
rm -rf ${PWD}/cfg
rm -rf ${PWD}/local

# Remove dependencies folders
rm -rf ${PWD}/reqs

# Remove deployment scripts and files
rm -f ${deploy_script}
rm -f ${undeploy_script}
rm -f Dockerfile.tpl
rm -f Dockerfile
rm -f .env
