# SCO/SO/API

This module takes care of documenting and exposing interfaces for the end-user to interact with the inner modules from a single point.

# Deployment

## Development env (venv)

```
cd deploy
# Specific module deployment
./venv-deploy.sh -s api
```

## Production env (Docker)

```
cd deploy
./docker-deploy.sh -s api
```

## Production env (Kubernetes)

NB: this is TODO work

# API

OpenAPI specs available under http://127.0.0.1:50101/api/docs
