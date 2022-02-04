# SCO/SO/LCM

This module takes care of the life-cycle management of all services.

# Deployment

## Development env (venv)

```
cd deploy
# Specific module deployment
./venv-deploy.sh -s lcm
```

## Production env (Docker)

```
cd deploy
./docker-deploy.sh -s lcm
```

## Production env (Kubernetes)

NB: this is TODO work

# API

```
MODL="lcm"
PORT="50105"

# Common

## Base method
curl http://127.0.0.1:${PORT}/${MODL}

# NS

## List running instances
curl http://127.0.0.1:${PORT}/${MODL}/ns
curl http://127.0.0.1:${PORT}/${MODL}/ns?id=<ns_instance_id>

## Instantiate new NS
curl http://127.0.0.1:${PORT}/${MODL}/ns -X POST -H "Content-Type: application/json" --data '{"ns-name": "<ns_name>", "instance-name": "...", "vim-id": "<vim_id>"}'

curl http://127.0.0.1:${PORT}/${MODL}/ns -X POST -H "Content-Type: application/json" --data '{"ns-name": "hackfest_proxycharm-ns
", "instance-name": "proxy-test", "vim-id": "b2f0b1b4-52a0-4434-8268-4bccc2e9cbd3"}'
### curl 'http://192.168.33.111/osm/nslcm/v1/ns_instances_content' -X POST -H 'Accept: application/json' -H 'Content-Type: application/json; charset=UTF-8' -H 'Authorization: Bearer H2bjCCPMsYhSB9SHanfeF4j1hIMquiy2' --data-raw '{"nsName":"test1","nsDescription":"test1","nsdId":"dbdab671-7d87-426a-bcf5-a2b6b4fc65c3","vimAccountId":"b2f0b1b4-52a0-4434-8268-4bccc2e9cbd3"}'

curl http://127.0.0.1:${PORT}/${MODL}/ns -X POST -H "Content-Type: application/json" --data '{"ns-name": "hackfest_proxycharm-ns", "instance-name": "proxy-test", "vim-id": "b2f0b1b4-52a0-4434-8268-4bccc2e9cbd3"}'

## Delete running instance
curl -X DELETE http://127.0.0.1:${PORT}/${MODL}/ns/<ns_instance_id>

# VNF

## List running instances
curl http://127.0.0.1:${PORT}/${MODL}/vnf
curl http://127.0.0.1:${PORT}/${MODL}/vnf?id=<vnf_instance_id>
```
