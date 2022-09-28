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
    if [[ $(basename ${PWD}) == "deploy" ]] && [[ -d "common" ]] && [[ -L cfg ]]; then
        echo "Reading env vars..."
    else
        error_msg="Cannot read env vars (due to a possible inconsistent status at /deploy or ${modl_base}/deploy\n"
	error_msg+="Attempting forced cleaning... However, check if the container was removed"
	text_error "${error_msg}"
	return
    fi
    # fetch_env_vars "${module}/deploy/env"
    # DEPRECATED: no longer using ${module}/deploy/env files
    # env_file=${module}/deploy/env
    env_file="${PWD}/../cfg/modules.yaml"
    deployed_module_dockerfile="${module}/deploy/docker/${docker_file}"

    if [[ ! -f "${env_file}" ]]; then
        error_msg="No deployment files found for module: \"${modl_base}\"\n"
        error_msg+="Missing file (among others): $(realpath ${deployed_module_dockerfile})"
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
        fetch_env_vars "${env_file}"
        fetch_env_vars_names
        # Export env vars so that envsubst can do its magic (replace_vars function)
        for env_var in "${ENV_VARS[@]}"; do
            export ${env_var}
        done
    fi
}

function remove_env_vars_setup() {
    # Clean symlinks necessary for reading the env vars
    if [[ $(basename ${PWD}) == "deploy" ]]; then
        ln_dir="common"
        if [[ -d ${ln_dir} ]]; then
            rm -rf ${ln_dir}
        fi
        if [[ -L cfg ]]; then
            rm cfg
        fi
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
        ./${undeploy_script} ${module} || true
        cd $current
    fi
}


function undeploy_modules() {
    # $MODULE: module name passed by parameter
    # $module: module name iterated from all modules
    for module in ${PWD}/../logic/modules/*; do
        modl_base=$(basename $module)
        modl_cont="so-${modl_base}"
        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $modl_base == $MODULE ]); then
            if [ -d ${module} ]; then
                title_info "Undeploying module \"${modl_base}\""
		running_container=$(docker ps -a | grep ${modl_cont})
                if [ ! "${running_container}" ]; then
                    text_warning "Module \"${modl_base}\" not deployed"
		fi
                if [[ "${running_container}" || ${FORCE} == "true" ]]; then
                    setup_env_vars "${module}"
                    setup_modl_undeploy_folder "${module}"
                fi
                # Reset the flag that indicates a module should be skipped
                MODULE_SKIP=0
	    fi
        fi
    done
    # This is a general setup, not just per module. Maybe it is best to keep it
    # remove_env_vars_setup
}

undeploy_modules
