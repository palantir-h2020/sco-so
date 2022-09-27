# SCO/SO/POL

This module takes care of the alerting of specific conditions related to the metrics that are taken from the virtual network services.

# Deployment

## Development env (venv)

```
cd deploy
# Specific module deployment
./venv-deploy.sh -s pol
```

## Production env (Docker)

```
cd deploy
./docker-deploy.sh -s pol
```

## Production env (Kubernetes)

NB: this is TODO work

# API

```
MODL="pol"
PORT="50108"

# Common

## Base method
curl http://127.0.0.1:${PORT}/${MODL}

# Alerts

## Registered alerts
curl http://127.0.0.1:${PORT}/${MODL}/alerts

## Register new alert with the values to monitor
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/alerts -d '{"alert-name": "__so_pol__df", "threshold": "2", "operator": "<=", "time-validity": "5", "hook-type": "kafka/webhook", "hook-endpoint": "http://127.0.0.1:${PORT}/${MODL}/notification"}'

# Metrics

## Metrics associated to alerts
curl http://127.0.0.1:${PORT}/${MODL}/metrics

## Activate background monitoring on the metric associated to the alert

### Note: both have the same "metric-name" -- the one registered above
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"xnf-id": "172.28.2.27:9100", "xnf-ip": "172.28.2.27", "metric-name": "__so_pol__date", "metric-command": "date +%s"}'

## Compare?
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/events -d '{"alert-name": "__so_pol__date", "metric-name": "__so_pol__date"}'
```
