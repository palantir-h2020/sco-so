#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


## ===========================================================================
##
## description     Undeploy the PALANTIR stack in the Kubernetes environment.
## author          Carolina Fernandez <carolina.fernandez@i2cat.net>
## date            2021/05/20
## version         0.1
## usage           ./kubernetes-undeploy.sh [-h] |
##                                          [-s ${module_name}]
##                                     -h: Print help
##                                     -s: Select a specific module
## notes           N/A
## bash_version    5.0-6ubuntu1.1
##
## ===========================================================================


current=$PWD

source deploy-vars.sh
source deploy-opts.sh


function setup_subc_deploy_folder() {
    module="$1"
    subc_deploy_path=${module}/deploy/kubernetes

    if [ -f ${subc_deploy_path}/${undeploy_script} ]; then
        title_info "Undeploying module: ${subc_base}"
        cd ${subc_deploy_path}
        ./${undeploy_script} || true
        cd $current
    fi

    # If all resources are within the namespace, its removal would be enough
    # However, we will explicitly remove each yaml file for increased reliance
    kubectl delete -f ${PWD}/kubernetes/${k8s_namespace}
}

#function undeploy_docker_registry() {
#    title_info "Undeploying Docker registry"
#    docker rm -f k8s-registry
#    docker image rm registry:2
#    docker tag docker_so_lcm:latest localhost:5000/docker_so_lcm
#}

function undeploy_modules() {
    for module in ${PWD}/../logic/modules/*; do
        subc_base=$(basename $module)

        if [ -z $MODULE ] || ([ ! -z $MODULE ] && [ $subc_base == $MODULE ]); then
            setup_subc_deploy_folder "${module}"
        fi
    done
}


undeploy_modules
# Decide whether to uncomment (if so, all previously registered images
# will vanish and it takes some time to register them)
#undeploy_docker_registry
