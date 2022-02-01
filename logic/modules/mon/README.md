# SCO/SO/MON

This module takes care of the monitoring of the virtual network services.

# Installation

```

```

# Deployment

```

```

## venv

```
cd deploy
./deploy.sh -s mon

*NOTE*: Get the openverso key on its directory /logic/modules/mon/data/key/openverso
```

# API

```
MODL="mon"
PORT="50106"

# Run API

$cd sco-so-venv/logic/modules/mon/src
$python3 main.py

# Common

## Base method
curl http://127.0.0.1:${PORT}/${MODL}

# Metrics

## VIM metrics
curl http://127.0.0.1:${PORT}/${MODL}/vim
curl http://127.0.0.1:${PORT}/${MODL}/vim\?vim-id\=d762daf2-5e62-4bf4-b979-718b8349ed81

## VNF metrics
curl http://127.0.0.1:${PORT}/${MODL}/vnf

## Prometheus targets
### *Note*: the file located at "logic/modules/mon/deploy/docker/local/prometheus-targets.json" is modified to add, replace or delete Prometheus targets. This file is delivered empty on purpose, and after adding new targets it should follow a format like this:
### [{"labels": {"job": "vnfs", "group": "vnfs", "env": "prod"}, "targets": ["10.10.10.11:9100", ..., "10.10.10.20:9100"]}]

curl http://127.0.0.1:${PORT}/${MODL}/targets
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/targets -d '{"url": "target-ip-or-fqdn:9090"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:${PORT}/${MODL}/targets -d '{"current-url": "target-ip-or-fqdn:9090", "new-url": "10.10.10.11:9090"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE http://127.0.0.1:${PORT}/${MODL}/targets -d '{"url": "target-ip-or-fqdn:9090"}'

## Prometheus targets metrics
curl http://127.0.0.1:${PORT}/${MODL}/targets/metrics

## VNF prometheus metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"vnf-id": "172.28.2.146:9100", "vnf-ip": "172.28.2.146", "metric-name": "node_netstat_Ip_Forwarding"}'

curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"vnf-id": "172.28.2.146:9100", "vnf-ip": "172.28.2.146", "metric-name": "node_netstat_Ip_Forwarding"}'

## VNF remote command metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/vnf -d '{"vnf-id": "172.28.2.146:9100", "vnf-ip": "172.28.2.146", "metric-name": "list", "metric-command": "ls"}'

## VNF prometheus-pushgateway metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/pushgateway -d '{"vnf-id": "172.28.2.146:9100", "metric-name": "disk_space", "metric-value": "660"}'

```
