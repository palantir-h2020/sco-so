# SCO/SO/MON

This module takes care of the monitoring of the virtual network services.

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

```
MODL="mon"
PORT="50106"

# Common

## Base method
curl http://127.0.0.1:${PORT}/${MODL}

# Metrics

## Infrastructure metrics
curl http://127.0.0.1:${PORT}/${MODL}/infra
curl http://127.0.0.1:${PORT}/${MODL}/infra\?id\=d762daf2-5e62-4bf4-b979-718b8349ed81

## xNF metrics
curl http://127.0.0.1:${PORT}/${MODL}/xnf

## Prometheus targets
### *Note*: the file located at "logic/modules/mon/deploy/docker/local/prometheus-targets.json" is modified to add, replace or delete Prometheus targets. This file is delivered empty on purpose, and after adding new targets it should follow a format like this:
### [{"labels": {"job": "xnfs", "group": "xnfs", "env": "prod"}, "targets": ["10.10.10.11:9100", ..., "10.10.10.20:9100"]}]

curl http://127.0.0.1:${PORT}/${MODL}/targets
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/targets -d '{"url": "target-ip-or-fqdn:9090"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:${PORT}/${MODL}/targets -d '{"current-url": "target-ip-or-fqdn:9090", "new-url": "10.10.10.11:9090"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE http://127.0.0.1:${PORT}/${MODL}/targets -d '{"url": "target-ip-or-fqdn:9090"}'

## Prometheus targets metrics
curl http://127.0.0.1:${PORT}/${MODL}/targets/metrics

## xNF prometheus metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"xnf-id": "172.28.2.146:9100", "xnf-ip": "172.28.2.146", "metric-name": "node_netstat_Ip_Forwarding"}'

curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"xnf-id": "172.28.2.146:9100", "xnf-ip": "172.28.2.146", "metric-name": "node_netstat_Ip_Forwarding"}'

## xNF remote command metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/xnf -d '{"xnf-id": "172.28.2.146:9100", "xnf-ip": "172.28.2.146", "metric-name": "list", "metric-command": "ls"}'

## xNF prometheus-pushgateway metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/pushgateway -d '{"xnf-id": "172.28.2.146:9100", "metric-name": "disk_space", "metric-value": "660"}'

```
