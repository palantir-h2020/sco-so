# SCO/SO/PKG

This module takes care of handling all packages.

# Deployment

## Development env (venv)

```
cd deploy
# Specific module deployment
./venv-deploy.sh -s pkg
```

## Production env (Docker)

```
cd deploy
./docker-deploy.sh -s pkg
```

## Production env (Kubernetes)

NB: this is TODO work

# API

```
MODL="pkg"
PORT="50107"

# Common

## Base method
curl http://127.0.0.1:${PORT}/${MODL}

# NS

## List packages
curl http://127.0.0.1:${PORT}/${MODL}/ns
curl http://127.0.0.1:${PORT}/${MODL}/ns?id=<ns_package_id>

# VNF

## List packages
curl http://127.0.0.1:${PORT}/${MODL}/vnf
curl http://127.0.0.1:${PORT}/${MODL}/vnf?id=<vnf_package_id>
```
