# SCO/SO/CFG

This module centralises all system-wide configuration (e.g. regarding tenants, infrastructures, topologies and so on), allowing both modification and retrieval.

# Deployment

## Development env (venv)

```
cd deploy
# Specific module deployment
./venv-deploy.sh -s cfg
```

## Production env (Docker)

```
cd deploy
./docker-deploy.sh -s cfg
```

## Production env (Kubernetes)

NB: this is TODO work

# API

```
MODL="cfg"
PORT="50103"

# Common

## Base method
curl http://127.0.0.1:${PORT}/${MODL}

# Network topology/landscape

## List the current network landscape
curl http://127.0.0.1:${PORT}/${MODL}/network-topology
```
