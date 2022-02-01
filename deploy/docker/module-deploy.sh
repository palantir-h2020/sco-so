#!/bin/bash

# Copyright 2021-present i2CAT
#
# Licensed under ???


# Corresponds to the $MODE argument, indicating to only generate Docker images
build_only=$1

docker_image_prefix="sco_so"

# Copy utils-related dependencies and sources to the module's context
common_reqs_path="${PWD}/../../../../common/deploy/reqs"
mkdir -p ${PWD}/reqs/common
if [[ -d ${common_reqs_path} ]]; then
    if [[ $(ls ${common_reqs_path} | wc -l) -gt 0 ]]; then
        cp -Rp ${common_reqs_path}/* ${PWD}/reqs/common/
    fi
fi
common_logic_path="${PWD}/../../../../common"
if [[ -d ${common_logic_path} ]]; then
    cp -Rp ${common_logic_path} .
fi

# Copy module-related dependencies and sources to the module's context
subc_reqs_path="${PWD}/../reqs"
mkdir -p ${PWD}/reqs/local
if [[ -d ${subc_reqs_path} ]]; then
    if [[ $(ls ${subc_reqs_path} | wc -l) -gt 0 ]]; then
        cp -Rp ${subc_reqs_path}/* ${PWD}/reqs/local/
    fi
fi
subc_logic_path="${PWD}/../../src"
if [[ -d ${subc_logic_path} ]]; then
    cp -Rp ${subc_logic_path} .
fi

# Copy local-related configuration for the module
# and use sample configuration files when needed
subc_cfg_path="${PWD}/../../cfg"
if [[ -d ${subc_cfg_path} ]]; then
    cp -Rp ${subc_cfg_path} .
    for cfg_file in $(ls ${PWD}/cfg/*); do
        cfg_file_nosample="${cfg_file/.sample/}"
        if [[ "${cfg_file}" == *.sample ]] && [[ ! -f ${cfg_file_nosample} ]]; then
            mv $cfg_file $cfg_file_nosample
        fi
    done
fi

# Copy deployment local-related files (such as common scripts
# or cfg files) in order to be used
subc_loc_path="${PWD}/../local"
if [[ -d ${subc_loc_path} ]]; then
    cp -Rp ${subc_loc_path} .
fi

# Deployment upon generation/build of images
if [[ "${build_only}" != "build" ]] && [[ -f docker-compose.yml ]]; then
    docker-compose up -d
    docker-compose ps
else
    # Build the image only if not already present (two rows: headers & image)
    if [[ $(docker image ls ${docker_image_prefix}_${SO_MODL_NAME} | wc -l) -lt 2 ]]; then
        # Explicitly stating the Dockerfile name, even if the default option
        docker build -t ${docker_image_prefix}_${SO_MODL_NAME} -f Dockerfile .
    fi
fi
