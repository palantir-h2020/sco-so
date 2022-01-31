#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


#
# DOCKER REGISTRY
#

docker_registry_port="30010"
docker_registry_url="docker-registry:${docker_registry_port}"

#
# DEPLOYMENT (COMMON)
#

deploy_script="module-deploy.sh"
undeploy_script="module-undeploy.sh"

#
# DOCKER DEPLOYMENT
#

docker_compose="docker-compose.yml"
docker_file="Dockerfile"

#
# KUBERNETES DEPLOYMENT
#

k8s_configmap="configmap.yaml"
k8s_deployment="deployment.yaml"
k8s_namespace_name="sco-so"
k8s_namespace="namespace.yaml"
