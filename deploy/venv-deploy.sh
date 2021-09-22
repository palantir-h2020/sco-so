#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


## ===========================================================================
##
## description     Deploy a PALANTIR stack subcomponent using venv.
##                   This is used for testing purposes
## author          Carolina Fernandez <carolina.fernandez@i2cat.net>
## date            2021/09/11
## version         0.1
## usage           ./venv-deploy.sh [-h] |
##                                     -s ${subcomponent_name}
##                                     -h: Print help
##                                     -s: Select a specific subcomponent
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
    subc_deploy_path=${subcomponent}/deploy/venv

    # Ensure the deployment subdirectory is created
    mkdir -p ${subc_deploy_path}

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

    # Copy the internal subcomponent's logic, then the common logic
    cp -Rp ${subcomponent}/src/* ${subc_deploy_path}/
    cp -Rp ${subcomponent}/cfg ${subc_deploy_path}/
    cd ${subc_deploy_path}
    for cfg_file in $(ls ${PWD}/cfg/*); do
        cfg_file_nosample="${cfg_file/.sample/}"
        if [[ "${cfg_file}" == *.sample ]] && [[ ! -f ${cfg_file_nosample} ]]; then
            mv $cfg_file $cfg_file_nosample
        fi
    done
    cd $current
    mkdir -p ${subc_deploy_path}/common
    cp -Rp ${subcomponent}/../../common/src/* ${subc_deploy_path}/common/
    touch ${subc_deploy_path}/pip_reqs
    cat ${subcomponent}/../../common/deploy/reqs/pip >> ${subc_deploy_path}/pip_reqs
    cat ${subcomponent}/deploy/reqs/pip >> ${subc_deploy_path}/pip_reqs
}

function setup_subc_deploy_folder() {
    subcomponent="$1"
    subc_deploy_path=${subcomponent}/deploy/venv

    mkdir -p ${subc_deploy_path}
    copy_replace_files "${subcomponent}"

    cd ${subc_deploy_path}
    python3 -m venv venv
    echo """
    Created: venv environment
    Start working on it with the following:

    cd ${subc_deploy_path}
    source venv/bin/activate 
    pip install -r pip_reqs
    python3 main.py

    When finished, either type:
    a) deactivate
    b) rm -rf ${subc_deploy_path}
    """
}

function deploy_subcomponents() {
    for subcomponent in ${PWD}/../logic/subcomponents/*; do
        subc_base=$(basename $subcomponent)
        subc_deploy_path=${subcomponent}/deploy/venv

        title_info "Deploying subcomponent: ${subc_base}"
        if [ -z $SUBCOMPONENT ] || ([ ! -z $SUBCOMPONENT ] && [ $subc_base == $SUBCOMPONENT ]); then
            setup_subc_deploy_folder "${subcomponent}" "${SUBCOMPONENT}"
        fi
    done
}


deploy_subcomponents
