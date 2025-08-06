
wDir  ?=${PWD}
sDir  ?=${wDir}/src
cDir  ?=${wDir}/sample-mcpServers-conf

myIP  ?=$(shell ip addr|grep 'inet '|grep -v '\.1/'|tr -s ' '|awk '{$$1=$$1};1'|cut -d ' ' -f 2|cut -d '/' -f 1|paste -sd "," -|sed s/addr://g)
#myIP ?=192.168.1.2

docker_network       ?=mcp-sandbox
port_mcpgateway      ?=8888-8889
port_inspector       ?=3000
port_inspector_proxy ?=3001
port_swagger         ?=8080
ALLOWED_ORIGINS      ?=http://${myIP}:${port_inspector}

# list of yaml files in ${cDir}
confs_yaml ?=$(shell find ${cDir} -type f | sort -f |  grep .yaml$$)

bash: _mk_vars
	${_envs} docker compose -f ./docker-compose.yaml exec mcp-gateway /bin/bash

start: docker-net-start _mk_vars
	${_envs} docker compose -f ./docker-compose.yaml up -d ${services}

stop:: _mk_vars
	${_envs} docker compose -f ./docker-compose.yaml down -v
stop::  docker-net-stop

docker-net-start:
	-docker network create ${docker_network}
docker-net-stop:
	-docker network rm ${docker_network}

docker-pull: _mk_vars
	${_envs} docker compose -f ./docker-compose.yaml pull ${services}

# hacks to join yaml files with document separator('---')
catConf:
	@awk 'FNR==1 && NR!=1 {print "---"}{print}' ${confs_yaml} | ./src/mergeYaml.py -e


# pack key=value pairs into _envs for easy docker compose ops
_mk_vars:
	$(eval _envs=$(shell echo "\
	wDir=${wDir} \
	sDir=${sDir} \
	cDir=${cDir} \
	ALLOWED_ORIGINS=${ALLOWED_ORIGINS} \
	port_inspector=${port_inspector} \
	port_inspector_proxy=${port_inspector_proxy} \
	port_mcpgateway=${port_mcpgateway} \
	port_swagger=${port_swagger} \
	docker_network=${docker_network} \
	" | cat))
#	@echo ${_envs} | sed 's/ /\n/g' | awk -F= '{print $$1,"=",$$2}' | sed 's/ //g'
