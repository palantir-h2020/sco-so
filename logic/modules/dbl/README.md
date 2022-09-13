# SCO/SO/DBL
DBL

This module is a Non-SQL DB (MongoDB) to serve the rest of the modules.

# Deployment

## Development env (venv)

```
cd deploy
# Specific module deployment
./venv-deploy.sh -s mon
```

## Production env (Docker)

```
cd deploy
./docker-deploy.sh -s mon
```

## Production env (Kubernetes)

NB: this is TODO work

# API

There is no custom API implemented on this one.

# Troubleshooting

## Container for so-dbl is continuously restarting

*Note: this may happen if you uncomment the "bind mount" rather than using the module.*

When meeting this issue and having no details under the `inspect` action (e.g., healthcheck being fine, etc), wait for the container to stop reloading after some time (maybe ~4 minutes).

If you see this in the logs:
```bash
{"t":{"$date":"..."},"s":"I",  "c":"CONTROL",  "id":...,   "ctx":"initandlisten","msg":"Shutting down","attr":{"exitCode":62}}
```

And/or see this when undeploying the docker-compose stack (with `docker-undeploy.sh`):
```bash
 Name               Command                State    Ports
---------------------------------------------------------
so-dbl   docker-entrypoint.sh --por ...   Exit 62 
```

Then, the folder named "_logic/modules/dbl/data_" is likely corrupted. You may remove it and reconstruct the database or, alternatively, play with the permissions adequately to get it to work (not tested).
