
img   ?=itaru2622/mcp:bookworm
wDir  ?=${PWD}
cName ?=mcp
myIP    ?=$(shell ip addr|grep 'inet '|grep -v '\.1/'|tr -s ' '|awk '{$$1=$$1};1'|cut -d ' ' -f 2|cut -d '/' -f 1|paste -sd "," -|sed s/addr://g)
#myIP   ?=192.168.1.2

docker_network=mcp-sandbox

port_mcp       ?=8888-8889
port_inspector ?=3000
port_inspector_proxy ?=3001
img_node ?=node:22-bookworm
inspector ?=npx @modelcontextprotocol/inspector
ALLOWED_ORIGINS ?=http://${myIP}:${port_inspector}

build:
	docker build -t ${img} .

bash:
	docker run --rm -it \
	-p ${port_mcp}:${port_mcp} \
	-e FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER=true \
	-e PYTHONPATH=${wDir} \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v ${wDir}:${wDir} -w ${wDir} \
	${img} /bin/bash

inspector:
	docker run -d --restart=always --name inspector  \
	-p ${port_inspector}:${port_inspector} -p ${port_inspector_proxy}:${port_inspector_proxy} \
        -e CLIENT_PORT=${port_inspector}       -e SERVER_PORT=${port_inspector_proxy} \
	-e HOST=0.0.0.0 \
	-e ALLOWED_ORIGINS=${ALLOWED_ORIGINS} \
	-e DANGEROUSLY_OMIT_AUTH=true \
        ${img_node} ${inspector}

start: docker-net-start
	wDir=${wDir} ALLOWED_ORIGINS=${ALLOWED_ORIGINS} \
	docker_network=${docker_network} \
	docker compose -f ./docker-compose.yaml up -d ${services}
stop::
	wDir=${wDir} ALLOWED_ORIGINS=${ALLOWED_ORIGINS} \
	docker compose -f ./docker-compose.yaml down -v
stop::  docker-net-stop

docker-net-start:
	-docker network create ${docker_network}
docker-net-stop:
	-docker network rm ${docker_network}
