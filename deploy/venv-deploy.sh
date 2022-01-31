#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


## ===========================================================================
##
## description     Deploy a PALANTIR stack module using venv.
##                   This is used for testing purposes
## author          Carolina Fernandez <carolina.fernandez@i2cat.net>
## date            2021/09/11
## version         0.1
## usage           ./venv-deploy.sh [-h] |
##                                     -s ${module_name}
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
source deploy-opts.sh


function copy_replace_files() {
    module="$1"
    modl_base=$(basename $module)
    modl_deploy_path=${module}/deploy/venv

    # Ensure the deployment subdirectory is created
    mkdir -p ${modl_deploy_path}

    if [[ -f "${module}/deploy/env" ]]; then
        # Reuse the general env file for the Docker environment
        cp -Rp ${module}/deploy/env ${modl_deploy_path}/.env
        echo "Reading env vars..."
        fetch_env_vars "${module}/deploy/env"
        fetch_env_vars_names
        # Export env vars so that envsubst can do its magic (replace_vars function)
        for env_var in "${ENV_VARS[@]}"; do
            export ${env_var}
        done
    else
        error_msg="No environment variables found for module=\"${modl_base}\""
        if [ ! -z $MODULE ] || ([ ! -z $MODULE ] && [ $modl_base == $MODULE ]); then
            text_error "${error_msg}"
        else
            error_exit "${error_msg}"
        fi
    fi

    # Copy the internal module's logic, then the common logic
    cp -Rp ${module}/src/* ${modl_deploy_path}/
    cp -Rp ${module}/cfg ${modl_deploy_path}/
    cd ${modl_deploy_path}
    for cfg_file in $(ls ${PWD}/cfg/*); do
        cfg_file_nosample="${cfg_file/.sample/}"
        if [[ "${cfg_file}" == *.sample ]] && [[ ! -f ${cfg_file_nosample} ]]; then
            mv $cfg_file $cfg_file_nosample
        fi
    done
    cd $current
    mkdir -p ${modl_deploy_path}/common
    cp -Rp ${module}/../../common/src/* ${modl_deploy_path}/common/
    touch ${modl_deploy_path}/pip_reqs
    cat ${module}/../../common/deploy/reqs/pip >> ${modl_deploy_path}/pip_reqs
    cat ${module}/deploy/reqs/pip >> ${modl_deploy_path}/pip_reqs
}

function setup_modl_deploy_folder() {
    module="$1"
    modl_deploy_path=${module}/deploy/venv

    mkdir -p ${modl_deploy_path}
    copy_replace_files "${module}"

    cd ${modl_deploy_path}
    python3 -m venv venv
    echo """
    Created: venv environment
    Start working on it with the following:

    cd ${modl_deploy_path}
    source venv/bin/activate 
    pip install -r pip_reqs
    python3 main.py

    When finished, either type:
    a) deactivate
    b) rm -rf ${modl_deploy_path}
    """
}

function deploy_modules() {
    for module in ${PWD}/../logic/modules/*; do
        modl_base=$(basename $module)
        modl_deploy_path=${module}/deploy/venv

        title_info "Deploying module: ${modl_base}"
        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $modl_base == $MODULE ]); then
            setup_modl_deploy_folder "${module}" "${MODULE}"
        fi
    done
}


deploy_modules
