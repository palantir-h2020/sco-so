#!/bin/bash

# Copyright 2021-present i2CAT
#
# Licensed under ???


# Corresponds to the $MODE argument, indicating to only generate Docker images
build_only=$1

docker_image_prefix="sco_so"

#
# deploy-opts.sh
#
function text_with_colour() {
    colour="$1"
    message="${@:2}"
    nocolour="\033[0m"
    printf "${colour}${message}${nocolour}\n"
}

function text_warning() {
    message=$@
    text_with_colour "\033[0;33m" "${message}"
}

function text_error() {
    message=$@
    text_with_colour "\033[1;31m" "${message}"
}

function error_exit() {
    text_error $@
    exit 1
}


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
gen_dep_path="${PWD}/../../../../../deploy"
modl_cfg_path="${PWD}/../../cfg"
if [[ -d ${gen_cfg_path} ]]; then
    if [[ ! -d ${modl_cfg_path} ]]; then
        mkdir -p ${modl_cfg_path}
    fi
    for cfg_file in $(ls ${gen_cfg_path}/*); do
        cfg_file_nosample="${cfg_file/.sample/}"
        basename_cfg_file_nosample=$(basename "${cfg_file_nosample}")
        # Verify cfg file is customised
        if [[ "${cfg_file}" == *.sample ]] && [[ ! -f ${cfg_file_nosample} ]]; then
            error_exit "Configuration file \"$(realpath ${cfg_file})\" is not personalised. To do so, copy the file into \"$(realpath ${cfg_file_nosample})\" and adjust the values"
        fi
        # Verify cfg file does not differ from upstream
        cfg_diff=$(python3 ${gen_dep_path}/diff_cfg.py "${cfg_file}")
        added_keys=$(echo ${cfg_diff} | python3 -c "import sys, json; print(json.load(sys.stdin).get(\"added-keys\"))")
        [[ "${added_keys}" == "[]" ]] && are_keys_added=0 || are_keys_added=1
        removed_keys=$(echo ${cfg_diff} | python3 -c "import sys, json; print(json.load(sys.stdin).get(\"removed-keys\"))")
        [[ "${removed_keys}" == "[]" ]] && are_keys_removed=0 || are_keys_removed=1
        # If any key is added or removed...
        # ...And this is not tackling the infra.yaml file (which can differ in its keys), show warning or error
        if ([[ ${are_keys_added} -eq 1 ]] || [[ ${are_keys_removed} -eq 1 ]]) && [[ ${basename_cfg_file_nosample} != "infra.yaml" ]]; then
            text_warning "Configuration file \"$(realpath ${cfg_file}.sample)\" is different to the local \"$(realpath ${cfg_file})\". Check these manually and adjust the values"
            if [[ ${are_keys_removed} -eq 1 ]]; then
                text_warning "\nConfiguration file \"$(realpath ${cfg_file}.sample)\" has removed the following keys:\n\t${removed_keys}\nIt is recommended to manually adjust the values in \"$(realpath ${cfg_file})\", but the deployment process will continue"
            fi
            if [[ ${are_keys_added} -eq 1 ]]; then
                error_exit "\nConfiguration file \"$(realpath ${cfg_file}.sample)\" has added the following keys:\n\t${added_keys}\nIt is mandatory to manually adjust the values in \"$(realpath ${cfg_file})\" before deploying"
            fi  
        fi
    done
    cp -Rp ${gen_cfg_path} .
    # Then, copy local-related configuration for the
    # module and use sample config files when needed
    if [[ ! -z $(ls -A ${modl_cfg_path}) ]]; then
        cp -Rp ${modl_cfg_path}/* cfg/
    fi
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
# or cfg files) in order to be used; then validate their existence
modl_loc_path="${PWD}/../local"
mkdir -p ${modl_loc_path}
if [[ -d ${modl_loc_path} ]]; then
    cp -Rp ${modl_loc_path} .
fi
# MON-specific
if [[ ${SO_MODL_NAME} == "mon" ]]; then
    gen_cfg_infra_file="${gen_cfg_path}/infra.yaml"
    mon_infra_files=$(cat ${gen_cfg_infra_file} | grep file | grep yaml | cut -d ":" -f2 | tr -d " " | tr -d "\"")
    for infra_file in ${mon_infra_files[$@]}; do
        infra_file_name=$(basename "${infra_file}")
        infra_cfg_file="${modl_loc_path}/${infra_file_name}"
        if [[ ! -f ${infra_cfg_file} ]]; then
          error_exit "Configuration file \"$(realpath ${infra_cfg_file})\" (requested by configuration file \"$(realpath ${gen_cfg_infra_file})\" to be able to extract metrics from the monitored infrastructures) is not personalised. To do so, copy the file into \"$(realpath ${modl_loc_path})\" and adjust the values"
        fi
    done
    gen_cfg_so_file="${gen_cfg_path}/so.yaml"
    mon_xnf_ssh_key=$(cat ${gen_cfg_so_file} | grep ssh-key  | cut -d ":" -f2 | tr -d " " | tr -d "\"")
    if [[ ! -s ${common_keys_path}/${mon_xnf_ssh_key} ]] ; then
        error_exit "SSH key \"$(realpath ${common_keys_path}/${mon_xnf_ssh_key})\" (requested by configuration file \"$(realpath ${gen_cfg_so_file})\" to be able to reach the monitored targets and extract data) is not defined yet. To do so, copy the proper SSH key into \"$(realpath ${common_keys_path})\""
    fi
    mon_xnf_ssh_key_permissions="-rw-rw-r--"
    if [[ $(stat -c %A ${common_keys_path}/${mon_xnf_ssh_key}) != "${mon_xnf_ssh_key_permissions}" ]]; then
        error_exit "SSH key \"$(realpath ${common_keys_path}/${mon_xnf_ssh_key})\" (requested by configuration file \"$(realpath ${gen_cfg_so_file})\" to be able to reach the monitored targets and extract data) has improper permissions. Please set these to \"${mon_xnf_ssh_key_permissions}\""
    fi
fi

# Deployment upon generation/build of images
if [[ "${build_only}" != "build" ]] && [[ -f docker-compose.yml ]]; then
    docker-compose -p ${SO_MODL_NAME} up -d
    docker-compose -p ${SO_MODL_NAME} ps
    if [[ ! -z ${SO_MODL_NAME} ]]; then
        running_container=$(docker ps -a | grep ${SO_MODL_NAME})
        if [[ ! "${running_container}" ]]; then
            error_exit "Module \"${SO_MODL_NAME}\" could not deploy. Try manually removing the \"$(realpath ${PWD}/Dockerfile)\" and re-deploying again"
        fi
    fi
else
    # Build the image only if not already present (two rows: headers & image)
    if [[ $(docker image ls ${docker_image_prefix}_${SO_MODL_NAME} | wc -l) -lt 2 ]]; then
        # Explicitly stating the Dockerfile name, even if the default option
        docker build -t ${docker_image_prefix}_${SO_MODL_NAME} -f Dockerfile .
    fi
fi

# MON-specific
if [[ ${SO_MODL_NAME} == "mon" ]]; then
    prometheus_targets_file="/share/prometheus-targets.json"
    prom_file_in_volume=$(docker exec -it so-mon ls ${prometheus_targets_file})
    prom_file_posix_code=$?
    # If not existing (or error, POSIX code != 0); copy the file "prometheus-targets.json" in the volume
    if [[ ${prom_file_in_volume} != *"${prometheus_targets_file}"* || ${prom_file_posix_code} -ne 0 ]]; then
        # This file is shared between so-mon and so-mon-prometheus
        docker cp ${modl_loc_path}/prometheus-targets.json so-${SO_MODL_NAME}:/share
    fi
fi
