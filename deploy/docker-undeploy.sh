#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


## ===========================================================================
##
## description     Undeploy the PALANTIR stack in Docker containers.
## author          Carolina Fernandez <carolina.fernandez@i2cat.net>
## date            2021/05/20
## version         0.1
## usage           ./docker-undeploy.sh [-h] |
##                                      [-s ${module_name}]
##                                     -h: Print help
##                                     -s: Select a specific module
## notes           N/A
## bash_version    5.0-6ubuntu1.1
##
## ===========================================================================


current=$PWD

ENV_VARS=()
ENV_VARS_NAMES=""
DEPLOY_DIR=$(realpath $(dirname $0))

source deploy-vars.sh
# Hack: export the required variables for undeployment
export docker_compose=${docker_compose}
source deploy-opts.sh


function setup_env_vars() {
    module="$1"
    subc_base=$(basename $module)
    subc_deploy_path=${module}/deploy/docker
    echo "Reading env vars..."
    fetch_env_vars "${module}/deploy/env"
}

function setup_subc_deploy_folder() {
    module="$1"
    subc_deploy_path=${module}/deploy/docker

    mkdir -p ${subc_deploy_path}
    # Copy undeployment script for module in each own's deploy/docker folder
    cp -Rp ${PWD}/docker/* ${subc_deploy_path}

    if [ -f ${subc_deploy_path}/${undeploy_script} ]; then
        if [ -f ${subc_deploy_path}/${docker_compose} ]; then
            title_info "Undeploying module: ${subc_base}"
            cd ${subc_deploy_path}
            ./${undeploy_script} || true
            cd $current
        fi
    fi
}


function undeploy_modules() {
    for module in ${PWD}/../logic/modules/*; do
        subc_base=$(basename $module)

        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $subc_base == $MODULE ]); then
	    #echo "UNDEPLOYING: ${module}"
            setup_env_vars "${module}"
            setup_subc_deploy_folder "${module}"
        fi
    done
}

undeploy_modules
