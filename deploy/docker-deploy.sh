#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


## ===========================================================================
##
## description     Deploy the PALANTIR stack in Docker containers.
## author          Carolina Fernandez <carolina.fernandez@i2cat.net>
## date            2021/05/20
## version         0.1
## usage           ./docker-deploy.sh [-h] |
##                                    [-s ${module_name}]
##                                    [-m ${mode}]
##                                     -h: Print help
##                                     -s: Select a specific module
##                                     -m: Use specific deployment mode
## notes           N/A
## bash_version    5.0-6ubuntu1.1
##
## ===========================================================================


current=$PWD

ENV_VARS=()
ENV_VARS_NAMES=""
DEPLOY_DIR=$(realpath $(dirname $0))

source deploy-vars.sh
source deploy-opts.sh


function docker_create_networks() {
  declare -a docker_preexisting_networks=("so-core" "so-db")
  for docker_network in "${docker_preexisting_networks[@]}"; do
      docker network create ${docker_network}
  done
}

function copy_replace_files() {
    module="$1"
    subc_base=$(basename $module)
    subc_deploy_path=${module}/deploy/docker

    if [[ -f "${module}/deploy/env" ]]; then
        # Reuse the general env file for the Docker environment
        cp -Rp ${module}/deploy/env ${subc_deploy_path}/.env
        echo "Reading env vars..."
        fetch_env_vars "${module}/deploy/env"
        fetch_env_vars_names
        # Export env vars so that envsubst can do its magic (replace_vars function)
        for env_var in "${ENV_VARS[@]}"; do
            export ${env_var}
        done
    else
        error_msg="No environment variables found for module=\"${subc_base}\""
        if [ ! -z $MODULE ] || ([ ! -z $MODULE ] && [ $subc_base == $MODULE ]); then
            text_error "${error_msg}"
        else
            error_exit "${error_msg}"
        fi
    fi

    # Copy deployment script for module in each own's deploy/docker folder
    cp -Rp ${PWD}/docker/* ${subc_deploy_path}
    # Copy deployment variables
    cp -Rp ${PWD}/deploy-vars.sh ${subc_deploy_path}
    # Copy Dockerfile template in each own's deploy/docker folder (if module does not have one already)
    if [ -f ${subc_deploy_path}/${docker_file} ]; then
        error_exit "File \"$(realpath ${subc_deploy_path}/${docker_file})\" already exists"
    fi
    if [ ! -f ${subc_deploy_path}/${docker_compose} ]; then
        error_exit "File \"$(realpath ${subc_deploy_path}/${docker_compose})\" does not exist"
    fi
    # Replace env vars as needed
    cp -Rp ${PWD}/docker/${docker_file}.tpl ${subc_deploy_path}/
    echo "Replacing env vars in template=\"${subc_deploy_path}/${docker_file}.tpl\"..."
    replace_vars "${subc_deploy_path}/${docker_file}.tpl"
}

function setup_subc_deploy_folder() {
    module="$1"
    subc_deploy_path=${module}/deploy/docker

    mkdir -p ${subc_deploy_path}
    copy_replace_files "${module}"
    if [ -f ${subc_deploy_path}/${deploy_script} ]; then
        cd ${subc_deploy_path}
        ./${deploy_script} ${MODE} || true
        cd $current
    fi
}

function deploy_modules() {
    # $MODULE: module name passed by parameter
    # $module: module name iterated from all modules
    for module in ${PWD}/../logic/modules/*; do
        subc_base=$(basename $module)
        subc_deploy_path=${module}/deploy/docker
        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $subc_base == $MODULE ]); then
	    if [ -d ${module} ]; then
                title_info "Deploying module: ${subc_base}"
                setup_subc_deploy_folder "${module}" "${MODULE}"
	    fi
        fi
    done
}


docker_create_networks
deploy_modules
