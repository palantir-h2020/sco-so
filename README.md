# SCO/SO API

The SCO/SO used in PALANTIR is a Security Orchestrator that consists of different subcomponents:

* `acl`: layer devoted to access control
* `api`: exposed public API endpoints
* `cfg`: exposes SCO/SO configuration
* `dbl`: layer devoted to database, keeping tables for each subcomponent
* `lcm`: the life-cycle management of all functionality, called from the API service
* `mon`: monitoring of the virtual network services, as well as the VIM
* `pkg`: handling of the packages for the virtual network functions and services
* `pol`: management of the received policies and its application onto the virtual network services
* `uti`: utilities, shared functionality copied into specific subcoponents

This component takes care of the onboarding of the Network Security Functions (NSFs) provided in the project and in managing its lifecycle, including its day-x configuration. To do so, some of these subcomponents will directly interact with the [OSM MANO](https://osm.etsi.org).

# Installation

## Prerequisites

All dependencies will be installed with the deployment scripts.

Regarding the infrastructure:

- A Docker registry can be optionally provided in the infrastructure.
  - If provided, this should go by the name of `docker-registry` and port `30010`. Each node in the Kubernetes cluster should point to this instance in the "/etc/hosts" file, so that it is accessible across the cluster.
  - Otherwise, it is expected that all Kubernetes nodes from the cluster can access any other node via SSH, so that SCO/SO can configure it.
- All Kubernetes nodes must be:
  - Accessible from each other using private key. The public key should be under ~/.ssh and it should be authorised in other nodes.
  - The user should be added to the Docker group OR have administration privileges without inputting a password.

# Deployment

## Docker

```
cd deploy
./docker-deploy.sh [-s <subcomponent>] [-m]
```

## Kubernetes

```
cd deploy
./kubernetes-deploy.sh [-s <subcomponent>] [-m] [-r]
```

# Default ports

* `acl`: 50100
* `api`: 50101
* `cfg`: 50102
* `dbl`: 50103
* `lcm`: 50104
* `mon`: 50105
* `pkg`: 50106
* `pol`: 50107

# API

## mon

### Common

#### Base method

```
curl http://127.0.0.1:50105/mon
```

#### VIM metrics

```
curl http://127.0.0.1:50105/mon/vim
```

#### VNF metrics

```
curl http://127.0.0.1:50105/mon/vnf
```

#### Prometheus targets

*Note*: the file located at "logic/subcomponents/mon/deploy/docker/local/prometheus-targets.json" is modified to add, replace or delete Prometheus targets. This file is delivered empty on purpose, and after adding new targets it should follow a format like this:

```
[{"labels": {"job": "vnfs", "group": "vnfs", "env": "prod"}, "targets": ["10.10.10.11:9100", ..., "10.10.10.20:9100"]}]
```

```
curl -i http://127.0.0.1:50105/mon/targets
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50105/mon/targets -d '{"url": "target-ip-or-fqdn:9090"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:50105/mon/targets -d '{"current-url": "target-ip-or-fqdn:9090", "new-url": "10.10.10.11:9090"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE http://127.0.0.1:50105/mon/targets -d '{"url": "target-ip-or-fqdn:9090"}'
```
