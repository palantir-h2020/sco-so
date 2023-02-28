# SCO/SO

The SO subcomponent takes care of the onboarding of the Network Security Functions (NSFs) provided in the project and in managing its lifecycle, including its day-x configuration. To do so, some of these modules will directly interact with the [OSM MANO](https://osm.etsi.org).

# Installation

## Prerequisites

All dependencies will be installed with the deployment scripts.

Before deployment, please check the following.

### Configuration

- Verify and adjust your custom configuration in all sample files under `./cfg`.
  - Copy first each ".yaml.sample" file into a ".yaml" file; then fill in with the proper data for your environment.
    - aac.yaml: no need to modify unless explicit changes are required.
    - db.yaml: no need to modify unless explicit changes are required.
    - dependencies.yaml: do not modify.
    - events.yaml: update with the IP and port of the Kafka to be used.
    - infra.yaml: update with the list of infrastructures (understood as Kubernetes cluster). Each entry shall include:
      - id: a manually provided UUID4 to identify them uniquely.
      - osm-vim-id: UUID4 given by OSM to the VIM (a dummy-vim used by the Kubernetes cluster), after [registering it there](https://osm.etsi.org/docs/user-guide/latest/05-osm-usage.html#adding-kubernetes-cluster-to-osm).
      - config.file: location of the kubeconfig file of the infrastructure, which is *relative to ./logic/modules/mon/deploy/local* and must be manually placed there.
      - tenant: name of the organisation who owns the cluster.
      - deployments: list of the supported deployment modes. Expected values: "cloud", "edge", "vcpe".
    - modules.yaml: no need to modify unless explicit changes are desired (e.g. changing ports for the services of SO). Modification not recommended (not fully tested).
    - so.yaml: update with the details for the SO:
      - so.ip: IP in which the SO runs.
      - osm.nbi: IP (host) in which OSM runs.
      - osm.vim.fallback: UUID4 given by OSM to the VIM that wants to be used as default cluster for deployment.
      - timings.interval: frequency (in seconds) of the requests produced by SO to OSM when fetching information on the status of the NSs and their actions.
      - timings.timeout.default: max time (in seconds) to wait for any generic operation (not contemplated below) to be completed in OSM.
      - timings.timeout.instantiation: max time (in seconds) to wait for the instantiation operation to be completed in OSM.
      - timings.timeout.action: max time (in seconds) to wait for the action (sent to a running NS) to be completed in OSM.
      - timings.timeout.scale: max time (in seconds) to wait for the scale operation (enacted on a running NS) to be completed in OSM. Not used at the moment.
      - timings.timeout.termination: max time (in seconds) to wait for the termination (stopping the running NS) operation (enacted on a running NS) to be completed in OSM.
      - timings.timeout.deletion: max time (in seconds) to wait for the deletion (removal of the running NS) operation (enacted on a running NS) to be completed in OSM.
      - events: enables/disables sending events to Kafka and indicates specific names for the topics (where the key is used within the code and the value is the actual name of the Kafka topic in use).
      - xnfs.general: defines the default user and location of the SSH key (which must be manually placed under the ./keys folder, relative to the root of the repository, and given "660" permissions).
- Check module-specific configuration under their folder, i.e. under `./logic/module/<module>/cfg`.
  - MON
    - mon.yaml (NOTE: only working for NSs running VMS in their VNFs):
      - prometheus: configuration for the IP (host), port, protocol and username for the Prometheus server instance + port used by Prometheus exporters in the targets.
      - metrics.targets.scrape_interval: frequency (in seconds) between retrieval of metrics from the targets.
      - metrics.targets.allowed_commands: whitelist of base UNIX commands allowed to be submitted by the operator when monitoring custom metrics.

### Infrastructure

- A Docker registry can be optionally provided in the infrastructure.
  - In this case:
    - Use name=`docker-registry` and port=`30010`.
    - Each node in the Kubernetes cluster should point to this instance in the `/etc/hosts` file, so that it is accessible across the cluster.
  - Otherwise, it is expected that all Kubernetes nodes from the cluster can access any other node via SSH, so that SCO/SO can configure it.
- All Kubernetes nodes must be accessible from each other using private key. The public key should be under ~/.ssh and it should be authorised in other nodes.
- The user should be added to the Docker group OR have administration privileges without inputting a password.

# Deployment

## Production env (Docker)

```
cd deploy
./docker-deploy.sh -s <module>
```

## Development env (venv)

*Note 1*: not up-to-date. Thus, it may not be fully working
*Note 2*: in "venv" deployment mode, the port for "dbl" is the default: 27017

```
cd deploy
# Direct access to venv
source deploy.sh
# Specific module deployment
./venv-deploy.sh -s <module>
```

## Production env (Kubernetes)

NB: not yet supported. Future work
```
cd deploy
./kubernetes-deploy.sh -s <module>
```

# Details

The SCO/SO used in PALANTIR is a Security Orchestrator that consists of different modules:

| Module |  Port | Docs | Status |
|:------------:|:-----:|:--------:|:------:|
| aac          | 50100 | [docs](logic/modules/aac/README.md) |  WIP   |
| api          | 50101 | [docs](logic/modules/api/README.md) |  WIP   |
| atr          | 50102 | [docs](logic/modules/atr/README.md) |  TBD   |
| cfg          | 50103 | [docs](logic/modules/cfg/README.md) |  WIP   |
| dbl          | 50104 | N/A                                 |  WIP   |
| lcm          | 50105 | [docs](logic/modules/lcm/README.md) |  WIP   |
| mon          | 50106 | [docs](logic/modules/mon/README.md) |  WIP   |
| pkg          | 50107 | [docs](logic/modules/pkg/README.md) |  WIP   |
| pol          | 50108 | [docs](logic/modules/pol/README.md) |  WIP   |
