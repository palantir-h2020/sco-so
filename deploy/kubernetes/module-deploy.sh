#!/bin/bash

# Copyright 2021-present i2CAT
#
# Licensed under ???


source deploy-vars.sh


function load_files() {
    template_files=("${k8s_configmap}")
    template_files+=("${k8s_deployment}")

    for template_file in "${template_files[@]}"; do
        if [ -f ${template_file} ]; then
            kubectl apply -f ${template_file}
        fi
    done
}


load_files
