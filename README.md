# simple-mcp-gateway

provides:
 - codes for simple MCP Gateways (MCP<=>REST, MCP<=>MCP)
 - Sample codes for MCP Client to access MCP Gateway.
 - Containsers for exuting and testing
     - Runtime env       to execute MCP gateways
     - MCP Inspector     to test/debug MCP gateways.
     - Swagger UI/Editor to test/debug OpenAPI spec for developing MCP<=>REST Gateway

pre-required:
 - docker, docker-compose

thanks to fastmcp (https://github.com/PrefectHQ/fastmcp).

## basic use

```bash
# starts docker containers
make start

# login to runtime container
make bash

# use following tools...
```

## Gateway (MCP <=> REST)

- source: src/mcp-gateway.py
- input:  OpenAPI spec file ( openapi v3.0 or 3.1), required json schema friendly format.

```bash
# usage
./src/mcp-gateway.py --help

usage: mcp-gateway.py [-h] [-s SPEC] [-b BASEURL]
                      [-a TOKEN] [--authHeader AUTHHEADER] [--tokenPrefix TOKENPREFIX] [--sslVerify | --no-sslVerify]
                      [-t TRANSPORT] [-p PORT] [-H HOST] [-l PATH] [-d LOG_LEVEL]

options:
  -h, --help                    show this help message and exit
  -s, --spec SPEC               OpenAPI spec file for gateway (json/yaml)
  -b, --baseURL BASEURL         baseURL to REST Server
  -a, --token TOKEN             bearer token to REST server
  --authHeader AUTHHEADER       Header name to fill token (default: 'Authorization')
  --tokenPrefix TOKENPREFIX     prefix to token string (default: 'Bearer ')
  --sslVerify, --no-sslVerify   SSL Verifyication      (default: True i.e. Verify)
  -t, --transport TRANSPORT     MCP server transport
  -p, --port PORT               MCP server port
  -H, --host HOST               MCP server host to listen
  -l, --path PATH               MCP server path to bind
  -d, --log_level LOG_LEVEL     MCP server log level
```

```bash
# example for REST service ( public/open area without auth ):
cat sample/openapi-specs/ghec-get-org-pruned-openapi31-validated.json | ./src/mcp-gateway.py -b https://api.github.com

# example for REST service with auth
cat sample/openapi-specs/ghec-get-org-pruned-openapi31-validated.json | ./src/mcp-gateway.py -b https://api.github.com -a YOUR_GITHUB_PAT
# Note this case has some security risk by proxying public/open <=> authorized space
```


## Gateway (MCP <=> MCP)

- source: src/double-mcp-gateway.py
- input:  MCP Server config

```bash
# usage
./src/double-mcp-gateway.py --help

usage: double-mcp-gateway.py [-h] [-s SPEC] [-t TRANSPORT] [-p PORT] [-H HOST] [-l PATH] [-d LOG_LEVEL]
options:
  -h, --help                   show this help message and exit
  -s, --spec SPEC              backend MCP server config (json|yaml|url)
  -t, --transport TRANSPORT    MCP server transport
  -p, --port PORT              MCP server port
  -H, --host HOST              MCP server host to listen
  -l, --path PATH              MCP server path to bind
  -d, --log_level LOG_LEVEL    MCP server log level

```

```bash
# example
cat sample/conf-mcpServers/echo.yaml | ./src/double-mcp-gateway.py
```

```bash
# yet another example (gateway ckan mcp server on docker).
export CKAN_URL=https://catalog.data.metro.tokyo.lg.jp
cat sample/conf-mcpServers/ckan-mcp-gateway.yaml | ./src/double-mcp-gateway.py -l /mcp/
```

## Sample MCP Server

- source: sample/mcp-servers/echo.py

```bash
fastmcp run --server-spec sample/mcp-servers/echo.py  --transport http --host 0.0.0.0 --port 8890
```

- source: sample/mcp-servers/fileprovider.py

```bash
./sample/mcp-servers/fileprovider.py --transport http --host 0.0.0.0 --port 8890 -f /tmp

# show helps
./sample/mcp-servers/fileprovider.py -h
usage: fileprovider.py [-h] [-f FOLDER] [-t TRANSPORT] [-p PORT] [-H HOST] [-l PATH] [-d LOG_LEVEL]

options:
  -h, --help            show this help message and exit
  -f, --folder FOLDER   toplevel folder to manage
  -t, --transport TRANSPORT
                        MCP server transport
  -p, --port PORT       MCP server port
  -H, --host HOST       MCP server host to listen
  -l, --path PATH       MCP server path to bind
  -d, --log_level LOG_LEVEL
                        MCP server log level
```


## Sample MCP Client

- source: src/llmclient.py

```bash
cat ./sample/conf-mcpServers/test-servers.yaml | sed 's/transport: streamable-http/transport: streamable_http/g' | ./src/llmclient.py
```

## Test all features:

```bash

# check/detect myIP to use.
make echo

# boot test environment (containers).
make start

# login to bash in container
make bash

# all below commands should be operated in mcp-gateway container

# boot MCP server with REST to MCP Gateway (for public spaces)
cat ./sample/openapi-specs/ghec-get-org-pruned-openapi31-validated.json | ./src/mcp-gateway.py -b https://api.github.com --port 8888 -l /mcp/

# boot MCP server with REST to MCP Gateway (with public and authorized spaces)
# Note this case has some security risk by proxying public/open <=> authorized space
# cat ./sample/openapi-specs/ghec-get-org-pruned-openapi31-validated.json | ./src/mcp-gateway.py -b https://api.github.com --port 8888 -l /mcp/ -a YOUR_GITHUB_PAT

# boot MCP server
fastmcp run --server-spec ./sample/mcp-servers/echo.py  --transport http --host 0.0.0.0 --port 8890 --path /mcp/

# boot mashup server all-in-one, with MCP to MCP Gateway
cat ./sample/conf-mcpServers/test-servers.yaml | ./src/double-mcp-gateway.py --port 8889 -l /mcp/

# test with client
cat ./sample/conf-mcpServers/test-servers.yaml  | sed 's/transport: streamable-http/transport: streamable_http/g' | ./src/llmclient.py
```

 - then access MCP Inspector with your browser ( i.e. http://${myIP}:3000/?MCP_PROXY_PORT=3001 )
 - setup MCP Inspector as below to interacts with the above features:

```
- URL:             http://${myIP}:8889/mcp/
- Transport:       Stremable HTTP
- Connection Type: Via Proxy

- Configuration:
   - Inspector Proxy Address: http://${myIP}:3001
```
