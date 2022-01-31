#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


## ===========================================================================
##
## description     Deploy the PALANTIR stack in the Kubernetes environment.
## author          Carolina Fernandez <carolina.fernandez@i2cat.net>
## date            2021/05/20
## version         0.1
## usage           ./kubernetes-deploy.sh [-h] |
##                                        [-s ${module_name}]
##                                        [-m ${mode}]
##                                        [-r ${registry}]
##                                     -h: Print help
##                                     -s: Select a specific module
##                                     -m: Use specific deployment mode
##                                     -r: Setup the Docker registry
## notes           N/A
## bash_version    5.0-6ubuntu1.1
##
## ===========================================================================


current=$PWD

docker_image_prefix="sco_so"
docker_registry_url="docker-registry:30010"
DOCKER_REGISTRY_USER="reguser"
DOCKER_REGISTRY_PASS="$(dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)"
ENV_VARS=()
ENV_VARS_NAMES=""
DEPLOY_DIR=$(realpath $(dirname $0))

source ${DEPLOY_DIR}/deploy-vars.sh
source ${DEPLOY_DIR}/deploy-opts.sh


function set_k8s_ns() {
    kubectl create ns ${k8s_namespace_name}
#    kubectl config set-context --current --namespace=sco-so
#    kubectl config use-context sco-so
}

#function unset_k8s_ns() {
#    kubectl config use-context default
#}

function load_ssh_agent_and_keys() {
    # Bad practice used to avoid defining explicit keypair
    eval $(ssh-agent) >/dev/null 2>&1
    ssh-add ~/.ssh/* >/dev/null 2>&1
}

function load_files() {
    module="$1"
    subc_k8s_deploy_path=${module}/deploy/kubernetes
    template_files=("${subc_k8s_deploy_path}/${k8s_configmap}")
    template_files+=("${subc_k8s_deploy_path}/${k8s_deployment}")

    for template_file in "${template_files[@]}"; do
        if [ -f ${template_file} ]; then
            kubectl -n ${k8s_namespace_name} apply -f ${template_file}
        fi
    done
}

function copy_replace_files() {
    module="$1"
    subc_base=$(basename $module)
    subc_docker_deploy_path=${module}/deploy/docker
    subc_k8s_deploy_path=${module}/deploy/kubernetes

    mkdir -p ${subc_k8s_deploy_path}
    # Copy deployment script for module in each own's deploy/kubernetes folder
    cp -Rp ${PWD}/kubernetes/*.sh ${subc_k8s_deploy_path}
    # Copy deployment variables
    cp -Rp ${PWD}/deploy-vars.sh ${subc_k8s_deploy_path}

    if [ -f "${module}/deploy/env" ]; then
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

    # Copy deployment.yaml template in each own's deploy/kubernetes folder (if module does not have one already)
    if [ ! -f ${subc_k8s_deploy_path}/${k8s_deployment}.tpl ] && [ ! -f ${subc_k8s_deploy_path}/${k8s_deployment} ]; then
        # Replace env vars as needed
        cp -Rp ${PWD}/kubernetes/${k8s_deployment}.tpl ${subc_k8s_deploy_path}/
        echo "Replacing env vars in template=\"${subc_k8s_deploy_path}/${k8s_deployment}.tpl\"..."
        replace_vars "${subc_k8s_deploy_path}/${k8s_deployment}.tpl"
    fi

    # Copy configmap.yaml template in each own's deploy/kubernetes folder (if module does not have one already)
    if [ ! -f ${subc_k8s_deploy_path}/${k8s_configmap}.tpl ] && [ ! -f ${subc_k8s_deploy_path}/${k8s_configmap} ]; then
        # Replace env vars as needed
        cp -Rp ${PWD}/kubernetes/${k8s_configmap}.tpl ${subc_k8s_deploy_path}/
        echo "Replacing env vars in template=\"${subc_k8s_deploy_path}/${k8s_configmap}.tpl\"..."
        replace_vars "${subc_k8s_deploy_path}/${k8s_configmap}.tpl"
        # Create intermediate file to fetch all related env vars
        configmap_int_file="${subc_k8s_deploy_path}/configmap-intermediate.yaml"
        touch ${configmap_int_file}
        for env_var in "${ENV_VARS[@]}"; do
            key=$(echo "${env_var}" | awk -F= '{print $1}')
            value=$(echo "${env_var}" | awk -F= '{print $2}')
            # Note: consider two spaces prepended at the beginning to successfully indent a valid YAML
            echo "  ${key}: '${value}'" >> ${configmap_int_file}
        done
        # Inject this file into the configmap.yaml template (note not .tpl is used here
        # because env vars were already replaced and the final file was generated)
        sed -i -e "/\${SO_MODL_ENV_VARS}/r ${configmap_int_file}" -e "//d" ${subc_k8s_deploy_path}/${k8s_configmap}
        chmod 764 ${subc_k8s_deploy_path}/${k8s_configmap}
    fi
}

function generate_docker_image() {
    # Generate Docker image, directly calling the Docker script
    # and passing the "build" value to the "mode" argument
    docker_deploy_flags="-m build $@"

    echo "Generating Docker image..."
    load_ssh_agent_and_keys
#    ssh -o StrictHostKeyChecking=no ${USER}@localhost -t ${DEPLOY_DIR}/docker-deploy.sh ${docker_deploy_flags}
   sudo su ${USER} -c "${DEPLOY_DIR}/docker-deploy.sh ${docker_deploy_flags}"
}

function tag_docker_image() {
    module="$1"
    subc_base=$(basename $module)

    echo "Tagging Docker image..."
    load_ssh_agent_and_keys
    ssh -o StrictHostKeyChecking=no ${USER}@localhost -t docker image tag ${docker_image_prefix}_${subc_base}:latest ${docker_registry_url}/${docker_image_prefix}_${subc_base}
#    sudo su ${USER} -c "docker image tag ${docker_image_prefix}_${subc_base}:latest ${docker_registry_url}/${docker_image_prefix}_${subc_base}"
}

function register_docker_image() {
    module="$1"
    subc_base=$(basename $module)

    echo "Pushing Docker image to local registry..."
    load_ssh_agent_and_keys
    docker_registry_url="${REGISTRY_NAME}:${REGISTRY_PORT}"
    # Get the password to login, prior to registering the Docker image
    docker_registry_decoded_password=$(kubectl -n sco-so get secret regcred -o jsonpath='{.data.\.dockerconfigjson}' | base64 --decode | python3 -c "import sys, json; print(json.load(sys.stdin)[\"auths\"][\":\"][\"password\"])")
    # Avoid strict key checking for fully automated access
    # Password can also be obtained from ${DOCKER_REGISTRY_PASSWORD}
    ssh -o StrictHostKeyChecking=no ${USER}@localhost -t docker login ${docker_registry_url} -u ${DOCKER_REGISTRY_USER} -p ${docker_registry_decoded_password} >/dev/null 2>&1
    ssh -o StrictHostKeyChecking=no ${USER}@localhost -t docker image push ${docker_registry_url}/${docker_image_prefix}_${subc_base}
#    sudo su ${USER} -c "docker image push ${docker_registry_url}/${docker_image_prefix}_${subc_base}"
}

function docker_pull_image_per_node() {
    # FIXME: this is a hack to preload generated image per Kubernetes node. This is not needed when
    # the private Docker registry is properly setup (reachable and accessible through credentials)
    # Plus, it is not working atm

    docker_registry_url="${REGISTRY_NAME}:${REGISTRY_PORT}"
    docker_registry_decoded_password=$(kubectl -n sco-so get secret regcred -o jsonpath='{.data.\.dockerconfigjson}' | base64 --decode | python3 -c "import sys, json; print(json.load(sys.stdin)[\"auths\"][\":\"][\"password\"])")
    load_ssh_agent_and_keys
    # Setup access to the Docker registry from all the Kubernetes nodes in the cluster
    for node_ip in $(kubectl get nodes -o jsonpath='{ $.items[*].status.addresses[?(@.type=="InternalIP")].address }'); do
        # Avoid strict key checking for fully automated access
        # Grant permissions on each node
        ssh -o StrictHostKeyChecking=no ${USER}@${node_ip} -t sudo usermod -aG docker ${USER}
        # Password can also be obtained from ${DOCKER_REGISTRY_PASSWORD}
        #ssh -o StrictHostKeyChecking=no ${USER}@${node_ip} -t docker login ${docker_registry_url} -u ${DOCKER_REGISTRY_USER} -p ${docker_registry_decoded_password} >/dev/null 2>&1
        ssh -o StrictHostKeyChecking=no ${USER}@${node_ip} -t docker login ${docker_registry_url} -u ${DOCKER_REGISTRY_USER} -p ${docker_registry_decoded_password}
        ssh -o StrictHostKeyChecking=no ${USER}@${node_ip} -t docker pull ${docker_registry_url}/${docker_image_prefix}_${subc_base}
    done

}

function setup_subc_deploy_folder() {
    module="$1"
    subc_base=$(basename $module)
    subc_k8s_deploy_path=${module}/deploy/kubernetes

    copy_replace_files "${module}"
#    load_files "${module}"
    # Create the common Kubernetes namespace
    kubectl -n ${k8s_namespace_name} apply -f ${PWD}/kubernetes/${k8s_namespace}

    if [ -f ${subc_k8s_deploy_path}/${deploy_script} ]; then
        # Creating, tagging and registering Docker images
        generate_docker_image "-s ${subc_base}"
        tag_docker_image ${subc_base}
        register_docker_image ${subc_base}
	# FIXME: hack (should not be needed when there is a private Docker registry)
	docker_pull_image_per_node

        text_info "Deploying module: ${subc_base}"
        cd ${subc_k8s_deploy_path}
        ./${deploy_script} || true
        cd $current
    fi
}

function grant_docker_permission_to_user() {
    # Grant permissions on, at least, the current node
    sudo usermod -aG docker ${USER}
    load_ssh_agent_and_keys
    # Create htpasswd file for authentication
    ssh -o StrictHostKeyChecking=no ${USER}@localhost -t docker pull registry:2.6.2 && \
	    ssh -o StrictHostKeyChecking=no ${USER}@localhost -t docker run --rm --entrypoint htpasswd registry:2.6.2 -Bbn ${DOCKER_REGISTRY_USER} ${DOCKER_REGISTRY_PASS} > ${USER}/docker_registry/auth/htpasswd
}

function deploy_docker_registry() {
    mkdir -p ${USER}/docker_registry/{certs,auth}
    #docker run -d -p ${docker_registry_port}:${docker_registry_port} --restart=always --name k8s-registry registry:2
    # Grant permissions to current user in Docker so as to create a transient container
    grant_docker_permission_to_user
    # Create certificate files for authentication
    openssl req -x509 -newkey rsa:4096 -days 365 -nodes -sha256 -keyout ${USER}/docker_registry/certs/tls.key -out ${USER}/docker_registry/certs/tls.crt -subj "/CN=docker-registry"
    # Kubernetes secrets for certificate and basic-auth
    kubectl -n ${k8s_namespace_name} create secret tls certs-secret --cert=${USER}/docker_registry/certs/tls.crt --key=${USER}/docker_registry/certs/tls.key
    kubectl -n ${k8s_namespace_name} create secret generic auth-secret --from-file=${USER}/docker_registry/auth/htpasswd
    # Create the Kubernetes volume, pod and service to create and expose the Docker registry to all Kubernetes cluster nodes
    kubectl -n ${k8s_namespace_name} apply -f ${DEPLOY_DIR}/kubernetes/docker-registry.yml
    # Create secret for the Docker registry
    kubectl -n ${k8s_namespace_name} create secret docker-registry regcred --docker-server=${REGISTRY_NAME}:${REGISTRY_PORT} --docker-username=${DOCKER_REGISTRY_USER} --docker-password=${DOCKER_REGISTRY_PASS} --docker-email=test@local
    # Update the default serviceaccount to allow pulling images by retrieving the credentials previously stored
    # Created by default when creating the NS
    kubectl -n ${k8s_namespace_name} patch serviceaccount default -p '{"imagePullSecrets": [{"name": "regcred"}]}'
}

function setup_docker_registry() {
    load_ssh_agent_and_keys
    hosts_edit_date=$(date '+%Y%m%d%H%M%S')
    # Setup access to the Docker registry from all the Kubernetes nodes in the cluster
    for node_ip in $(kubectl get nodes -o jsonpath='{ $.items[*].status.addresses[?(@.type=="InternalIP")].address }'); do
	# Avoid strict key checking for fully automated access
	# Remove previous docker-registry inputs and update
        ssh -o StrictHostKeyChecking=no ${USER}@${node_ip} "sudo sed -i\"_${hosts_edit_date}\" '/docker-registry/d' /etc/hosts"
        ssh -o StrictHostKeyChecking=no ${USER}@${node_ip} "echo \"$REGISTRY_IP $REGISTRY_NAME\" | sudo tee -a /etc/hosts"
        ssh -o StrictHostKeyChecking=no ${USER}@${node_ip} "sudo rm -rf /etc/docker/certs.d/$REGISTRY_NAME:${REGISTRY_PORT}; sudo mkdir -p /etc/docker/certs.d/$REGISTRY_NAME:${REGISTRY_PORT}; sudo chown ${USER}:${USER} -R /etc/docker/certs.d/$REGISTRY_NAME:${REGISTRY_PORT}"
        scp -o StrictHostKeyChecking=no ${USER}/docker_registry/certs/tls.crt ${USER}@${node_ip}:/etc/docker/certs.d/$REGISTRY_NAME:${REGISTRY_PORT}/ca.crt
    done
}

function setup_private_distributed_docker_registry() {
    title_info "Deploying Docker registry"
    #docker run -d -p ${docker_registry_port}:${docker_registry_port} --restart=always --name k8s-registry registry:2
    create_registry="false"
    if [[ ! $(kubectl -n ${k8s_namespace_name} get pod docker-registry-pod >/dev/null 2>&1) ]] && [[ ${REGISTRY} == "true" ]]; then
	create_registry="true"
    else
        echo "Already exists..."
    fi
    if [[ ${create_registry} == "true" ]]; then
        deploy_docker_registry
    fi
    echo "Waiting few seconds for the registry to be generated..."
    sleep 5
    registry_pod_ip=$(kubectl -n ${k8s_namespace_name} get pod docker-registry-pod -o=jsonpath='{.status.podIP}')
    registry_host_ip=$(kubectl -n ${k8s_namespace_name} get pod docker-registry-pod -o=jsonpath='{.status.hostIP}')
    registry_pod_port=$(kubectl -n ${k8s_namespace_name} get service docker-registry -o=jsonpath='{.spec.ports[0].nodePort}')
    export REGISTRY_NAME="docker-registry"
    export REGISTRY_IP="${registry_host_ip}"
    export REGISTRY_PORT="${registry_pod_port}"
    docker_registry_url="${REGISTRY_NAME}:${REGISTRY_PORT}"
    if [[ ${create_registry} == "true" ]]; then
        setup_docker_registry
    fi
}

function deploy_modules() {
    for module in ${PWD}/../logic/modules/*; do
        subc_base=$(basename $module)
        subc_k8s_deploy_path=${module}/deploy/kubernetes

        if [ -f ${subc_k8s_deploy_path}/${k8s_deployment} ]; then
            title_info "Deploying module: ${subc_base}"
        fi
        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $subc_base == $MODULE ]); then
            setup_subc_deploy_folder "${module}"
        fi
    done
}


set_k8s_ns
setup_private_distributed_docker_registry
deploy_modules
#unset_k8s_ns
