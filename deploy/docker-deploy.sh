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
MODULE_SKIP=0

source deploy-vars.sh
source deploy-opts.sh


function docker_install() {
    if [[ ! -x "$(command -v docker)" ]]; then
        echo "Installing Docker..."
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl gnupg lsb-release
        OS=$(echo "$(lsb_release -is)" | tr "[:upper:]" "[:lower:]")
        # Install GPG key
        curl -fsSL https://download.docker.com/linux/${OS}/gpg | sudo gpg --batch --yes --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        # Install Docker binary
        echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/${OS} \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        # Add current user to Docker
        sudo groupadd docker || true
        sudo usermod -aG docker $USER
        # Avoid logging in
        sudo chgrp docker $(which docker)
        sudo chmod g+s $(which docker)
        # Install docker-compose binary
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
}

function docker_create_networks() {
    declare -a docker_preexisting_networks=("so-core" "so-db")
    for docker_network in "${docker_preexisting_networks[@]}"; do
        if [ ! "$(docker network ls | grep ${docker_network})" ]; then
            docker network create ${docker_network}
        fi
    done
}

function copy_replace_files() {
    module="$1"
    modl_base=$(basename $module)
    modl_deploy_path=${module}/deploy/docker

    if [[ ! -f "${module}/deploy/env" ]]; then
        error_msg="No environment variables found for module: \"${modl_base}\"\n"
        error_msg+="Missing file: $(realpath ${module}/deploy/env)"
	# If no specific module is provided (via $MODULE), attempt all available modules to deploy
        if [[ -z $MODULE ]]; then
            text_error "${error_msg}. Skipping current module"
	    # Determine that this module is to be skipped if:
	    # (i) there is no envvars file; and (ii) no explicit module is defined
	    MODULE_SKIP=1
	# Otherwise, when asking for the specific deployment
        else
	    error_exit "${error_msg}"
	fi
	# NB: original checks
        #if [ ! -z $MODULE ] || ([ ! -z $MODULE ] && [ $modl_base == $MODULE ]); then
        #    text_error "${error_msg}"
        #else
        #    error_exit "${error_msg}"
        #fi
    else
        # Reuse the general env file for the Docker environment
        cp -Rp ${module}/deploy/env ${modl_deploy_path}/.env
        echo "Reading env vars..."
        fetch_env_vars "${module}/deploy/env"
        fetch_env_vars_names
        # Export env vars so that envsubst can do its magic (replace_vars function)
        for env_var in "${ENV_VARS[@]}"; do
            export ${env_var}
        done
    fi

    # Only continue when the module is not skipped
    if [ $MODULE_SKIP -eq 0 ]; then
        # Copy deployment script for module in each own's deploy/docker folder
        cp -Rp ${PWD}/docker/* ${modl_deploy_path}
        # Copy deployment variables
        cp -Rp ${PWD}/deploy-vars.sh ${modl_deploy_path}
        # Copy Dockerfile template in each own's deploy/docker folder (if module does not have one already)
        if [ -f ${modl_deploy_path}/${docker_file} ]; then
            error_msg="No Dockerfile found for module: \"${modl_base}\"\n"
            error_msg+="Missing file: $(realpath ${modl_deploy_path}/${docker_file})"
            error_exit "${error_msg}"
        fi
        if [ ! -f ${modl_deploy_path}/${docker_compose} ]; then
            error_msg="No docker-compose definition found for module: \"${modl_base}\"\n"
            error_msg+="Missing file: $(realpath ${modl_deploy_path}/${docker_compose})"
            error_exit "${error_msg}"
        fi
        # Replace env vars as needed
        cp -Rp ${PWD}/docker/${docker_file}.tpl ${modl_deploy_path}/
        echo "Replacing env vars in template: ${modl_deploy_path}/${docker_file}.tpl ..."
        replace_vars "${modl_deploy_path}/${docker_file}.tpl"
    fi
}

function setup_modl_deploy_folder() {
    module="$1"
    modl_deploy_path=${module}/deploy/docker
    mkdir -p ${modl_deploy_path}
    copy_replace_files "${module}"
    if [ $MODULE_SKIP -eq 0 ] && [ -f ${modl_deploy_path}/${deploy_script} ]; then
        cd ${modl_deploy_path}
        ./${deploy_script} ${MODE} || true
        cd $current
    fi
}

function deploy_modules() {
    # $MODULE: module name passed by parameter
    # $module: module name iterated from all modules
    for module in ${PWD}/../logic/modules/*; do
        modl_base=$(basename $module)
	modl_cont="so-${modl_base}"
        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $modl_base == $MODULE ]); then
	    if [ -d ${module} ]; then
                title_info "Deploying module: ${modl_base}"
	        if [ "$(docker ps -a | grep ${modl_cont})" ]; then
                    text_warning "Module: ${modl_base} already deployed"
                else
                    setup_modl_deploy_folder "${module}" "${MODULE}"
                fi
                # Reset the flag that indicates a module should be skipped
		MODULE_SKIP=0
	    fi
        fi
    done
}


docker_install
docker_create_networks
deploy_modules
