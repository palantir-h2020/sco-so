#!/bin/bash

# Copyright 2021-present i2CAT
#
# Licensed under ???


MODULE=$1

# Undeployment
if [[ -f ${docker_compose} ]] && [[ ! -z ${SO_MODL_NAME} ]]; then
    # Env vars can be used for the docker-compose.yaml file
    docker-compose -p ${SO_MODL_NAME} ps
    docker-compose -p ${SO_MODL_NAME} down
else
    # Otherwise, just attempt forceful removal
    modl_base=$(basename ${MODULE})
    docker rm -f "so-${modl_base}"
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
