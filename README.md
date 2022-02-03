# SCO/SO

The SO subcomponent takes care of the onboarding of the Network Security Functions (NSFs) provided in the project and in managing its lifecycle, including its day-x configuration. To do so, some of these modules will directly interact with the [OSM MANO](https://osm.etsi.org).

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

## Development env (venv)

*Note*: in "venv" deployment mode, the port for "dbl" is the default: 27017

```
cd deploy
# Direct access to venv
source deploy.sh
# Specific module deployment
./venv-deploy.sh -s <module>
```

## Production env (Docker)

NB: this is WIP for some modules
```
cd deploy
./docker-deploy.sh -s <module>
```

## Production env (Kubernetes)

NB: this is TODO work
```
cd deploy
./kubernetes-deploy.sh -s <module>
```

# Details

The SCO/SO used in PALANTIR is a Security Orchestrator that consists of different modules:

| Module |  Port | Docs | Status |
|:------------:|:-----:|:--------:|:------:|
| aac          | 50100 | [docs](logic/modules/aac/README.md) |  TBD   |
| api          | 50101 | [docs](logic/modules/api/README.md) |  WIP   |
| atr          | 50102 | [docs](logic/modules/atr/README.md) |  TBD   |
| cfg          | 50103 | [docs](logic/modules/cfg/README.md) |  TBD   |
| dbl          | 50104 | N/A |  WIP   |
| lcm          | 50105 | [docs](logic/modules/lcm/README.md) |  WIP   |
| mon          | 50106 | [docs](logic/modules/mon/README.md) |  WIP   |
| pkg          | 50107 | [docs](logic/modules/pkg/README.md) |  WIP   |
| pol          | 50108 | [docs](logic/modules/pol/README.md) |  TBD   |
