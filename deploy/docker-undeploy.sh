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
MODULE_SKIP=0

source deploy-vars.sh
# Hack: export the required variables for undeployment
export docker_compose=${docker_compose}
source deploy-opts.sh


function setup_env_vars() {
    module="$1"
    modl_base=$(basename $module)
    modl_deploy_path=${module}/deploy/docker
    echo "Reading env vars..."
    # fetch_env_vars "${module}/deploy/env"
    if [[ ! -f "${module}/deploy/env" ]]; then
        error_msg="No environment variables found for module: \"${modl_base}\"\n"
        error_msg+="Missing file: $(realpath ${module}/deploy/env)"
        # If no specific module is provided (via $MODULE), attempt all available modules to deploy
        if [[ -z $MODULE ]]; then
            text_error "${error_msg}. Skipping current module"
            # Determine that procedure for this module is to be skipped if:
            # (i) there is no envvars file; and (ii) no explicit module is defined
            MODULE_SKIP=1
        # Otherwise, when asking for the specific deployment
        else
            error_exit "${error_msg}"
        fi
    else
        fetch_env_vars "${module}/deploy/env"
    fi
}

function setup_modl_undeploy_folder() {
    module="$1"
    modl_deploy_path=${module}/deploy/docker
    mkdir -p ${modl_deploy_path}
    # Copy undeployment script for module in each own's deploy/docker folder
    cp -Rp ${PWD}/docker/* ${modl_deploy_path}
    if [ ! -f ${modl_deploy_path}/${undeploy_script} ] || [ ! -f ${modl_deploy_path}/${docker_compose} ]; then
        MODULE_SKIP=1
    fi
    if [ $MODULE_SKIP -eq 0 ]; then
        cd ${modl_deploy_path}
        ./${undeploy_script} || true
        cd $current
    fi
}


function undeploy_modules() {
    # $MODULE: module name passed by parameter
    # $module: module name iterated from all modules
    for module in ${PWD}/../logic/modules/*; do
        modl_base=$(basename $module)
        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $modl_base == $MODULE ]); then
            if [ -d ${module} ]; then
                title_info "Undeploying module: ${modl_base}"
                setup_env_vars "${module}"
                setup_modl_undeploy_folder "${module}"
                # Reset the flag that indicates a module should be skipped
                MODULE_SKIP=0
	    fi
        fi
    done
}

undeploy_modules
