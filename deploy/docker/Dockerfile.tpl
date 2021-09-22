# Note: this variable must be replaced before building the image
FROM python:3.8-slim AS so-${SO_SUBC_NAME}

# Copy local-related dependencies into container
RUN mkdir -p /opt/reqs/local
COPY ./reqs/local /opt/reqs/local
# Copy common-related dependencies into container
RUN mkdir -p /opt/reqs/common
COPY ./reqs/common /opt/reqs/common

WORKDIR /opt/
# Copy local-related sources into container
COPY ./src/ /opt/
# Copy common-related sources into container
RUN mkdir -p /opt/common
COPY ./common/src /opt/common/

# Copy local-related sources for the HTTP server into the common-related sources
# This is done to place the subcomponent's Flask blueprints into the specific
# folder in the common sources, acting as a drop-in plug-in
RUN mkdir -p /opt/blueprints
#COPY ./src/server/blueprints/* /opt/common/src/server/http/blueprints/
COPY ./src/server/blueprints/* /opt/blueprints/
# Copy common-related blueprints sources as well
COPY ./common/src/server/http/blueprints/* /opt/blueprints/

# Copy local-related configuration for the subcomponent
RUN mkdir -p /opt/cfg
COPY ./cfg /opt/cfg/

# Install pre-requisites
RUN apt-get update && \
    apt-get install -y python3-pip
RUN /usr/local/bin/python -m pip install --upgrade pip

WORKDIR /opt/reqs

# Note: the following folders should exist, as these provide
# stack-wide and component-local dependencies

## Install common-related requisites
RUN ([ -f common/pip ] && pip3 install -r common/pip) || true
RUN ([ -f common/apt ] && (cat common/apt | xargs apt-get install -y)) || true

## Install local-related requisites
RUN ([ -f local/pip ] && pip3 install -r local/pip) || true
RUN ([ -f local/apt ] && (cat local/apt | xargs apt-get install -y)) || true

COPY run.sh /opt/

WORKDIR /opt
CMD ["python3", "main.py"]
#ENTRYPOINT "/opt/run.sh"
