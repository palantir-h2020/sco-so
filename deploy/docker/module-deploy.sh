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
modl_reqs_path="${PWD}/../reqs"
mkdir -p ${PWD}/reqs/local
if [[ -d ${modl_reqs_path} ]]; then
    if [[ $(ls ${modl_reqs_path} | wc -l) -gt 0 ]]; then
        cp -Rp ${modl_reqs_path}/* ${PWD}/reqs/local/
    fi
fi
modl_logic_path="${PWD}/../../src"
if [[ -d ${modl_logic_path} ]]; then
    cp -Rp ${modl_logic_path} .
fi

# Copy common configuration first
gen_cfg_path="${PWD}/../../../../../cfg"
modl_cfg_path="${PWD}/../../cfg"
if [[ -d ${gen_cfg_path} ]]; then
  if [[ ! -d ${modl_cfg_path} ]]; then
    mkdir -p ${modl_cfg_path}
  fi
  cp -Rp ${gen_cfg_path} .
  # Then, copy local-related configuration for the
  # module and use sample config files when needed
  cp -Rp ${modl_cfg_path}/* cfg/
  for cfg_file in $(ls ${PWD}/cfg/*); do
      cfg_file_nosample="${cfg_file/.sample/}"
      if [[ "${cfg_file}" == *.sample ]] && [[ ! -f ${cfg_file_nosample} ]]; then
          mv $cfg_file $cfg_file_nosample
      fi
  done
fi

# Copy keys
common_keys_path="${PWD}/../../../../../keys"
mkdir -p ${PWD}/keys
if [[ -d ${common_keys_path} ]]; then
    cp -Rp ${common_keys_path}/* ${PWD}/keys/
fi

# Copy deployment local-related files (such as common scripts
# or cfg files) in order to be used
modl_loc_path="${PWD}/../local"
mkdir -p ${modl_loc_path}
if [[ -d ${modl_loc_path} ]]; then
    cp -Rp ${modl_loc_path} .
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
