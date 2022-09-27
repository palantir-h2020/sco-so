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

## Infrastructure
curl http://127.0.0.1:${PORT}/${MODL}/infra
curl http://127.0.0.1:${PORT}/${MODL}/infra\?id\=d762daf2-5e62-4bf4-b979-718b8349ed81

## All metrics

### Retrieve both generic and custom metrics
curl http://127.0.0.1:${PORT}/${MODL}/targets/metrics

## Custom metrics

### Register custom metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/xnf -d '{"xnf-id": "target-ip-or-fqdn:9100", "xnf-ip": "target-ip-or-fqdn", "metric-name": "ls", "metric-command": "ls"}'

### ???
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/pushgateway -d '{"xnf-id": "target-ip-or-fqdn:9100", "metric-name": "disk_space", "metric-value": "660"}'

## Generic metrics

### Manage generic metrics
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"xnf-id": "target-ip-or-fqdn:9100", "xnf-ip": "target-ip-or-fqdn", "metric-name": "node_disk_info"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"xnf-id": "target-ip-or-fqdn:9100", "xnf-ip": "target-ip-or-fqdn", "metric-name": "node_netstat_Ip_Forwarding"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:${PORT}/${MODL}/metrics -d '{"xnf-id": "target-ip-or-fqdn:9100", "xnf-ip": "target-ip-or-fqdn", "metric-name": "node_netstat_Ip_Forwarding"}'

## Prometheus management

### Manage Prometheus setup
curl http://127.0.0.1:${PORT}/${MODL}/targets
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/targets -d '{"url": "target-ip-or-fqdn:9100"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:${PORT}/${MODL}/targets -d '{"current-url": "target-ip-or-fqdn:9100", "new-url": "10.10.10.11:9100"}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE http://127.0.0.1:${PORT}/${MODL}/targets -d '{"url": "target-ip-or-fqdn:9100"}'

# Manually install Prometheus instance in the target
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/node -d '{"xnf-ip": ["target-ip-or-fqdn"]}'
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE http://127.0.0.1:${PORT}/${MODL}/metrics/node -d '{"xnf-ip": ["target-ip-or-fqdn"]}'

## Alerts

### Check alerts related to metrics
curl http://127.0.0.1:${PORT}/${MODL}/metrics/alerts

### Runs background monitoring on a metric (to be called from POL?)
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/background -d '{"xnf-id": "target-ip-or-fqdn:9100", "xnf-ip": "target-ip-or-fqdn", "metric-name": "ls", "metric-command": "ls"}'

#### TODO: TEST IF THESE WORK
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:${PORT}/${MODL}/metrics/xnf -d '{"xnf-id": "target-ip-or-fqdn:9100", "xnf-ip": "target-ip-or-fqdn", "metric-name": "ls", "metric-command": "free -m | head -2 | tail -1 | awk '{print $2}'"}
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50108/pol/metrics -d '{"xnf-id": "target-ip-or-fqdn:9100", "xnf-ip": "target-ip-or-fqdn", "metric-name": "__so_pol__date", "metric-command": "free -m | head -2 | tail -1 | awk \'{print $2}\'"}'
```
