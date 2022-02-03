# Note: this variable must be replaced before building the image
FROM python:3.8-slim AS so-${SO_MODL_NAME}

ENV SO_ROOT="/opt"

# Copy local-related dependencies into container
RUN mkdir -p ${SO_ROOT}/reqs/local
COPY ./reqs/local ${SO_ROOT}/reqs/local
# Copy common-related dependencies into container
RUN mkdir -p ${SO_ROOT}/reqs/common
COPY ./reqs/common ${SO_ROOT}/reqs/common

WORKDIR ${SO_ROOT}/
# Copy local-related sources into container
COPY ./src/ ${SO_ROOT}/
# Copy common-related sources into container
RUN (mkdir -p ${SO_ROOT}/common || true)
COPY ./common/src ${SO_ROOT}/common/

# Copy local-related sources for the HTTP server into the common-related sources
# This is done to place the server's blueprints into the specific
# folder in the common sources, acting as a drop-in plug-in
RUN mkdir -p ${SO_ROOT}/blueprints
#COPY ./src/server/blueprints/* ${SO_ROOT}/common/src/server/http/blueprints/
COPY ./src/server/blueprints/ ${SO_ROOT}/blueprints/
# Copy common-related blueprints sources as well
COPY ./common/src/server/http/blueprints/ ${SO_ROOT}/blueprints/

# Copy local module-related configuration for the module
RUN mkdir -p ${SO_ROOT}/cfg
COPY ./cfg ${SO_ROOT}/cfg/
# Copy local deployment-related configuration for the module
RUN mkdir -p ${SO_ROOT}/deploy/local
COPY ./local ${SO_ROOT}/deploy/local/

# Install pre-requisites
RUN apt-get update && \
    apt-get install -y python3-pip vim
RUN /usr/local/bin/python -m pip install --upgrade pip
# General steps
RUN touch ~/.vimrc

WORKDIR ${SO_ROOT}/reqs

# Note: the following folders should exist, as these provide
# stack-wide and component-local dependencies

## Install common-related requisites
RUN ([ -f common/pip ] && pip3 install -r common/pip) || true
RUN ([ -f common/apt ] && (cat common/apt | xargs apt-get install -y)) || true

## Install local-related requisites
RUN ([ -f local/pip ] && pip3 install -r local/pip) || true
RUN ([ -f local/apt ] && (cat local/apt | xargs apt-get install -y)) || true

WORKDIR ${SO_ROOT}
#CMD ["python3", "main.py"]
CMD ["sleep", "infinity"]
