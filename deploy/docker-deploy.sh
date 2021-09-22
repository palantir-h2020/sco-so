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
##                                    [-s ${subcomponent_name}]
##                                    [-m ${mode}]
##                                     -h: Print help
##                                     -s: Select a specific subcomponent
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


function copy_replace_files() {
    subcomponent="$1"
    subc_base=$(basename $subcomponent)
    subc_deploy_path=${subcomponent}/deploy/docker

    if [[ -f "${subcomponent}/deploy/env" ]]; then
        # Reuse the general env file for the Docker environment
        cp -Rp ${subcomponent}/deploy/env ${subc_deploy_path}/.env
        echo "Reading env vars..."
        fetch_env_vars "${subcomponent}/deploy/env"
        fetch_env_vars_names
        # Export env vars so that envsubst can do its magic (replace_vars function)
        for env_var in "${ENV_VARS[@]}"; do
            export ${env_var}
        done
    else
        error_msg="No environment variables found for subcomponent=\"${subc_base}\""
        if [ ! -z $SUBCOMPONENT ] || ([ ! -z $SUBCOMPONENT ] && [ $subc_base == $SUBCOMPONENT ]); then
            text_error "${error_msg}"
        else
            error_exit "${error_msg}"
        fi
    fi

    # Copy deployment script for subcomponent in each own's deploy/docker folder
    cp -Rp ${PWD}/docker/* ${subc_deploy_path}
    # Copy deployment variables
    cp -Rp ${PWD}/deploy-vars.sh ${subc_deploy_path}
    # Copy Dockerfile template in each own's deploy/docker folder (if subcomponent does not have one already)
    if [ ! -f ${subc_deploy_path}/${docker_file} ] && [ -f ${subc_deploy_path}/${docker_compose} ]; then
        # Replace env vars as needed
        cp -Rp ${PWD}/docker/${docker_file}.tpl ${subc_deploy_path}/
        echo "Replacing env vars in template=\"${subc_deploy_path}/${docker_file}.tpl\"..."
        replace_vars "${subc_deploy_path}/${docker_file}.tpl"
    fi
}

function setup_subc_deploy_folder() {
    subcomponent="$1"
    subc_deploy_path=${subcomponent}/deploy/docker

    mkdir -p ${subc_deploy_path}
    copy_replace_files "${subcomponent}"
    if [ -f ${subc_deploy_path}/${deploy_script} ]; then
        cd ${subc_deploy_path}
        ./${deploy_script} ${MODE} || true
        cd $current
    fi
}

function deploy_subcomponents() {
    for subcomponent in ${PWD}/../logic/subcomponents/*; do
        subc_base=$(basename $subcomponent)
        subc_deploy_path=${subcomponent}/deploy/docker

        if [ -f ${subc_deploy_path}/${docker_compose} ]; then
            title_info "Deploying subcomponent: ${subc_base}"
        fi
        if [ -z $SUBCOMPONENT ] || ([ ! -z $SUBCOMPONENT ] && [ $subc_base == $SUBCOMPONENT ]); then
            setup_subc_deploy_folder "${subcomponent}" "${SUBCOMPONENT}"
        fi
    done
}


deploy_subcomponents
