#!/usr/bin/env bash

docker network create palantir-monitoring-network --driver bridge
# Pull image
docker pull prom/prometheus

cat <<EOF>>prometheus.yml
global:
  external_labels:
    monitor: codelab-monitor
  scrape_interval: 15s
scrape_configs:
  - job_name: "server"
    scrape_interval: 5s
    static_configs:
      - targets:
        - "palantir-prometheus-server:9090"
        labels:
          group: "prometheus-central"
  - job_name: "vnfs"
    scrape_interval: 10s
    scrape_timeout: 8s
    file_sd_configs:
    - files:
        - "prometheus-targets.json"
      refresh_interval: 5s
EOF

cat <<EOF>>prometheus-targets.json
[
 {
   "labels": {
     "job": "vnfs",
     "group": "vnfs",
     "env": "prod"
   },
   "targets": [
     "palantir-prometheus-pushgateway:9091"
  ]
 }
]
EOF

docker run --name palantir-prometheus-server -itd\
    --network "palantir-monitoring-network" \
    -p 9090:9090 \
    -v ${PWD}/prometheus.yml:/etc/prometheus/prometheus.yml \
    -v ${PWD}/prometheus-targets.json:/etc/prometheus/prometheus-targets.json \
    prom/prometheus

