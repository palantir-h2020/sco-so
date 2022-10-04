#!/bin/bash

# Copyright 2021-present i2CAT
# All rights reserved


#
# VISUAL STYLES
#

function text_with_colour() {
    colour="$1"
    message="${@:2}"
    nocolour="\033[0m"
    printf "${colour}${message}${nocolour}\n"
}

function title_with_colour() {
    colour="$1"
    message="${@:2}"
    TASK_NUMBER=$((${TASK_NUMBER}+1))
    bold=$(tput bold)
    normal=$(tput sgr0)
    text=$(text_with_colour ${colour} "TASK ${TASK_NUMBER} [ ${message} ]")
    printf "\n${bold}${text}${normal}\n"
    printf "*%.0s" {1..123}
    printf "\n"
}

function title_info() {
    message=$@
    title_with_colour "\033[1;34m" "${message}"
}

function text_info() {
    message=$@
    text_with_colour "\033[0;37m" "${message}"
}

function text_success() {
    message=$@
    text_with_colour "\033[1;32m" "${message}"
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


#
# ENV VARS
#

ENV_VARS=()
ENV_VARS_NAMES=""
DEPLOY_DIR=$(realpath $(dirname $0))

# Replace environment variables in the provided array of template files
function replace_specific_vars() {
    template_files=( "$@" )
    for template_file in "${template_files[@]}"; do
        template_file_subst="${template_file%%.tpl}"
        echo "Replacing variables: $(realpath ${template_file}) > $(realpath ${template_file_subst})"
        # New method: fine-grained, only substitutes a specific set of variables under the .env file
        # and others defined in the "fetch_env_vars" method. Example:
        # $ envsubst '${SO_MODL_NAME} ${SO_MODL_API_PORT}' < $template_file > $template_file_subst
        envsubst "${ENV_VARS_NAMES}" < $template_file > $template_file_subst
    done
}

# Find template files and replace environment variables in them
function replace_vars() {
    #title_info "Substituting env vars, generating configuration files"
    # Important: some *.tpl files are replaced through the above generate-xx-template.sh files. The blocks below will also
    # replace these but do not generate any useful (nor harmful) output

    # Find all template files under the specific environment directory and replace env vars
    #IFS= readarray -t template_env_files < <(find ${DEPLOY_DIR}/env/$ENV/ -name "*.tpl" -print)
    #[[ ${#template_env_files[@]} -gt 0 ]] && title_info "Replacing $ENV environment variables into templates"
    #replace_specific_vars "${template_env_files[@]}"
    replace_specific_vars "$1"
    #check_exit_code_for_task
}

# Load environment-related variables from a given file
function fetch_env_vars() {
    # Environment variables
    DEPLOY_ENV_VARS=$1
    [[ ! -f $DEPLOY_ENV_VARS ]] && error_exit "File with environment variables ($DEPLOY_ENV_VARS) not found"

    # DEPRECATED: no longer using ${MODULE}/deploy/env files
    # Read only export non-commented and "key=value"-like lines
    # while IFS="=" read -r key value; do
    #     if ! [[ -z $key ]] && ! [[ -z $value ]] && ! [[ "$key" =~ ^#.*$ ]]; then
    #         # Remove leading and trailing whitespacess on value
    #         value="${value#"${value%%[![:space:]]*}"}"
    #         value="${value%"${value##*[![:space:]]}"}"
    #         line="${key}=${value}"
    #         export "$line"
    #         ENV_VARS+=("$line")
    #     fi
    # done < "$DEPLOY_ENV_VARS"

    # Create symlinks necessary for reading the env vars
    ln_dir="common"
    if [[ $(basename ${PWD}) == "deploy" ]]; then
	[[ ! -L ${PWD}/cfg ]] && ln -s ../cfg ${PWD}/cfg
        mkdir -p ${ln_dir}
	[[ ! -L ${PWD}/${ln_dir}/config ]] && ln -s ${PWD}/../logic/common/src/config ${ln_dir}
	[[ ! -L ${PWD}/${ln_dir}/exception ]] && ln -s ${PWD}/../logic/common/src/exception ${ln_dir}
	[[ ! -L ${PWD}/${ln_dir}/server ]] &&  ln -s ${PWD}/../logic/common/src/server ${ln_dir}
	[[ ! -L ${PWD}/${ln_dir}/utils ]] && ln -s ${PWD}/../logic/common/src/utils ${ln_dir}
    fi
    # Fetch container names and ports from cfg/modules.yaml
    ENV_VARS+=($(python3 fetch_env_vars.py ${MODULE}))

    # Add specific environment variables (related to paths, for proper replacement in files)
    ENV_VARS+=("DEPLOY_DIR=${DEPLOY_DIR}")
    if [[ ! -z ${docker_registry_url} ]]; then
        ENV_VARS+=("DOCKER_REGISTRY_URL=${docker_registry_url}")
    fi

    echo "${ENV_VARS[@]}"
}

function fetch_env_vars_names() {
    ENV_VARS_NAMES=""
    for var in "${ENV_VARS[@]}"; do
        var=$(echo $var | sed -r -e "s/\n//g")

        separator="="
        # Key is everything to the left-hand side of the first occurrence of the separator
        key=${var%%"$separator"*}
        # Note: some variables may be like "key= value" and must account for the whitespace
        key=${key%%"$separator" *}

        # Handle format with care
        ENV_VARS_NAMES+='$'${key}' '
    done

    # Remove trailing whitespaces on the generated string
    ENV_VARS_NAMES="${ENV_VARS_NAMES%"${ENV_VARS_NAMES##*[![:space:]]}"}"
}


#
# DIRECTORIES AND OTHERS
#

function get_dirs_under_path() {
    path=$1
    dirs=()
    for dir in $path/*; do
        if [[ -d $dir ]]; then
            dirs+=($(basename $dir))
        fi
    done
    echo ${dirs[@]}
}

#
# USAGE INFO AND PARSING LOGIC
#

function usage() {
    echo -e "Usage: $0 [OPTIONS]"
    echo -e "Deploy or undeploy the SO modules"
    echo -e "  OPTIONS"
    echo -e "     -h / --help:    print this help"
    echo -e "     [-s]:           operate on a specific module from the following: $(get_dirs_under_path ../logic/module)"
    echo -e "     [-f]:           force operation overriding basic checks"
    if [[ $0 == *"-deploy"* ]]; then
      echo -e "     [-m]:           only create container images (\"build\") or create+instantiate (default)"
    fi
    if [[ $0 == *"kubernetes"* ]]; then
      echo -e "     [-r]:           setup the Docker registry"
    fi
}


# Module to deploy
MODULE=""
# Mode: "build" (generate Docker images) or deploy (generate+instantiate, default)
MODE=""
REGISTRY="false"
FORCE="false"
# Counter with the number of selected options
OPTIONS_SELECTED=0

while getopts ":s:m:-: rfh" o; do
    case "${o}" in
        s)
            MODULE="${OPTARG}"
            OPTIONS_SELECTED=$((${OPTIONS_SELECTED}+1))
            ;;
        m)
            MODE="${OPTARG}"
            OPTIONS_SELECTED=$((${OPTIONS_SELECTED}+1))
            ;;
        r)
            REGISTRY="true"
            ;;
        f)
            FORCE="true"
            ;;
        -)
            [ "${OPTARG}" == "help" ] && usage && exit 0
            ;;
        :)
            echo "Option -$OPTARG requires an argument" >&2
            usage && exit 1
            ;;
        \?)
            echo -e "Invalid option: '-$OPTARG'\n" >&2
            usage && exit 1
            ;;
        h)
            usage && exit 0
            ;;
        *)
            ;;
    esac
done

if [ ! -z "$1" ] && [ ${OPTIONS_SELECTED} -eq 0 ]; then
    echo -e "Invalid param: '$@'\n" >&2
    usage && exit 1
fi
