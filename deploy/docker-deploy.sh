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

DOCKER_NETWORK_DB="so-db"
DOCKER_NETWORK_CORE="so-core"
DOCKER_VOLUME_DB="so-db"
DOCKER_VOLUME_MON="so-mon"

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

function docker_setup_iproute_cmd() {
    docker_net="${1}"
    docker_br_so_net_id=$(docker network inspect -f '{{.Id}}' ${docker_net} | cut -c1-12)
    docker_br_so_net_gw=$(docker network inspect -f '{{range.IPAM.Config}}{{.Gateway}}{{end}}' ${docker_net})
    docker_br_so_net_sub=$(docker network inspect -f '{{range.IPAM.Config}}{{.Subnet}}{{end}}' ${docker_net})
    docker_br_so_net_sub_mask=${docker_br_so_net_sub%:*}
    docker_br_so_net_sub_mask=${docker_br_so_net_sub_mask##*/}
    docker_br_so_net_cidr="${docker_br_so_net_gw}/${docker_br_so_net_sub_mask}"
    docker_if_docker0_ip_route=$(ip route show ${docker_br_so_net_cidr} | wc -l)
    if [[ ${docker_if_docker0_ip_route} -eq 0 ]]; then
        echo "sudo ip addr add dev br-${docker_br_so_net_id} ${docker_br_so_net_cidr}"
    fi
}

function docker_config_networks() {
    # Check for Docker bridges, in case of misconfiguration
    docker_if_docker0_config="172.17.0.0/16"

    ## Example
    # sudo ip addr add dev docker0 172.17.0.1/16
    # sudo ip addr add dev br-829ce0f80e44 172.28.0.1/16
    # sudo ip addr add dev br-b49b248f967b 172.29.0.1/16

    ## Check 1st routing rule
    docker_if_docker0_ip_route=$(ip route show ${docker_if_docker0_config} | wc -l)
    if [[ ${docker_if_docker0_ip_route} -eq 0 ]]; then
        echo "Creating Docker interfaces \"docker0\""
        sudo ip addr add dev docker0 ${docker_if_docker0_config}
    fi

    ## Check 2nd routing rule
    docker_br_so_net_cidr=$(docker_setup_iproute_cmd "${DOCKER_NETWORK_CORE}")
    if [[ ! -z ${docker_br_so_net_cidr} ]]; then
        echo "Creating Docker bridges \"${DOCKER_NETWORK_CORE}\""
        $(eval ${docker_br_so_net_cidr})
    fi

    ## Check 3rd routing rule
    docker_br_db_net_cidr=$(docker_setup_iproute_cmd "${DOCKER_NETWORK_DB}")
    if [[ ! -z ${docker_br_db_net_cidr} ]]; then
        echo "Creating Docker bridges \"${DOCKER_NETWORK_DB}\""
        $(eval ${docker_br_db_net_cidr})
    fi
}

function docker_create_networks() {
    declare -a docker_preexisting_networks=("${DOCKER_NETWORK_CORE}" "${DOCKER_NETWORK_DB}")
    for docker_network in "${docker_preexisting_networks[@]}"; do
        if [ ! "$(docker network ls | grep ${docker_network})" ]; then
            echo "Creating Docker network \"${docker_network}\""
            docker network create ${docker_network}
        fi
    done
}

function docker_create_volumes() {
    declare -a docker_preexisting_volumes=("${DOCKER_VOLUME_DB}" "${DOCKER_VOLUME_MON}")
    for docker_volume in "${docker_preexisting_volumes[@]}"; do
        if [ ! "$(docker volume ls | grep ${docker_volume})" ]; then
            echo "Creating Docker volume \"${docker_volume}\""
            docker volume create ${docker_volume}
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
        # 2022/07/22: NEW
        # Copy Dockerfile template in each own's deploy/docker folder (if module does not have one already)
        if [ ! -f ${modl_deploy_path}/${docker_file} ]; then
            # Replace env vars as needed
            cp -Rp ${PWD}/docker/${docker_file}.tpl ${modl_deploy_path}/
            echo "Replacing env vars in template: ${modl_deploy_path}/${docker_file}.tpl ..."
            replace_vars "${modl_deploy_path}/${docker_file}.tpl"
        fi
        # 2022/07/22: NOTE THIS IS THE ORIGINAL CODE
        # Copy Dockerfile template in each own's deploy/docker folder (if module does not have one already)
        if [ ! -f ${modl_deploy_path}/${docker_file} ]; then
            error_msg="No Dockerfile found for module: \"${modl_base}\"\n"
            error_msg+="Missing file: $(realpath ${modl_deploy_path}/${docker_file})"
            error_exit "${error_msg}"
        fi
        if [ ! -f ${modl_deploy_path}/${docker_compose} ]; then
            error_msg="No docker-compose definition found for module: \"${modl_base}\"\n"
            error_msg+="Missing file: $(realpath ${modl_deploy_path}/${docker_compose})"
            error_exit "${error_msg}"
        fi
#       # 2022/07/22: COMMENTED
#        # Replace env vars as needed
#        cp -Rp ${PWD}/docker/${docker_file}.tpl ${modl_deploy_path}/
#        echo "Replacing env vars in template: ${modl_deploy_path}/${docker_file}.tpl ..."
#        replace_vars "${modl_deploy_path}/${docker_file}.tpl"
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
    MODULE_FOUND=0
    for module in ${PWD}/../logic/modules/*; do
        modl_base=$(basename $module)
        modl_cont="so-${modl_base}"
        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $modl_base == $MODULE ]); then
            if [ -d ${module} ]; then
                title_info "Deploying module \"${modl_base}\""
                if [ "$(docker ps -a | grep ${modl_cont})" ]; then
                    text_warning "Module \"${modl_base}\" already deployed"
                else
                    setup_modl_deploy_folder "${module}" "${MODULE}"
                fi
                # Reset the flag that indicates a module should be skipped
                MODULE_SKIP=0
                MODULE_FOUND=1
            fi
        fi
    done
    if ([ ! -z $MODULE ] && [ ${MODULE_FOUND} -eq 0 ]); then
        text_warning "Module \"${MODULE}\" does not exist"
    fi
}


docker_install
# Create volumes if not there
docker_create_volumes
# Create networks if not there
docker_create_networks
deploy_modules
# Needed in case Docker networking failed in the environment
docker_config_networks
