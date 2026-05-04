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

- source: src/gateways/mcp-gateway.py
- input:  OpenAPI spec file ( openapi v3.0 or 3.1), required json schema friendly format.

```bash
# usage

fastmcp run --server-spec src/gateways/mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8888 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir examples/openapi-specs  \
            -- -s openAPI.yaml -b ...

./src/gateways/mcp-gateway.py --help
usage: mcp-gateway.py [-h] [-s SPEC] [-b BASEURL]
                      [-a TOKEN] [--authHeader AUTHHEADER] [--tokenPrefix TOKENPREFIX] [--sslVerify | --no-sslVerify]
                      [-l LOG_LEVEL]
options:
  -h, --help                    show this help message and exit
  -s, --spec SPEC               OpenAPI spec file for gateway (json/yaml)
  -b, --baseURL BASEURL         baseURL to REST Server
  -a, --token TOKEN             bearer token to REST server
  --authHeader AUTHHEADER       Header name to fill token (default: 'Authorization')
  --tokenPrefix TOKENPREFIX     prefix to token string (default: 'Bearer ')
  --sslVerify, --no-sslVerify   SSL Verifyication      (default: True i.e. Verify)
  -l, --log-level LOG_LEVEL     MCP server log level
```

```bash
# example for REST service ( public/open area without auth ):
fastmcp run --server-spec src/gateways/mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8888 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir examples/openapi-specs  \
            -- -s examples/openapi-specs/ghec-get-org-pruned-openapi31-validated.json \
               -b https://api.github.com

# example for REST service with auth
fastmcp run --server-spec src/gateways/mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8888 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir examples/openapi-specs  \
            -- -s examples/openapi-specs/ghec-get-org-pruned-openapi31-validated.json \
               -b https://api.github.com  -a YOUR_GITHUB_PAT -l DEBUG
# Note this case has some security risk by proxying public/open <=> authorized space
```


## Gateway (MCP <=> MCP)

- source: src/gateways/double-mcp-gateway.py
- input:  MCP Server config

```bash
# usage
fastmcp run --server-spec src/gateways/double-mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8889 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir ./examples/conf-mcpServers \
            -- -s mcp-server-config.yaml

./src/gateways/double-mcp-gateway.py --help
usage: double-mcp-gateway.py [-h] [-s SPEC] [-l LOG_LEVEL]
options:
  -h, --help                   show this help message and exit
  -s, --spec SPEC              backend MCP server config (json|yaml|url)
  -l, --log_level LOG_LEVEL    MCP server log level

```

```bash
# example
fastmcp run --server-spec src/gateways/double-mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8889 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir ./examples/conf-mcpServers \
            -- -s examples/conf-mcpServers/echo.yaml
```

```bash
# yet another example (gateway ckan mcp server on docker).
export CKAN_URL=https://catalog.data.metro.tokyo.lg.jp
fastmcp run --server-spec src/gateways/double-mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8889 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir ./examples/conf-mcpServers \
            -- -s examples/conf-mcpServers/ckan-mcp-gateway.yaml
```

## Sample MCP Server

- source: examples/src/mcpservers/echo.py

```bash
fastmcp run --server-spec examples/src/mcpservers/echo.py  --transport http --host 0.0.0.0 --port 8890
```

- source: examples/src/mcpservers/fileprovider.py

```bash
folder=/tmp/test  \
fastmcp run --server-spec ./examples/src/mcpservers/fileprovider.py:mcp --transport http --host 0.0.0.0 --port 8890 --path /mcp/ -l DEBUG --reload


# show helps for fileprovider.py
python -c "from fileprovider import help; help()"

usage: -c [-h] [--folder str] [--mount str] [--transport str]
Settings for the app.

NG:  use commandline options.
OK:  compatible with env style, like below:

folder=/tmp/test2 fastcmp run this:mcp --host 0.0.0.0 --port 8888 --path /mcp/ --transport streamable-http 
folder=/tmp/test2 mount=/mcp/ transport=streamable-http   uvicorn this:app --host 0.0.0.0 --port 8888

to print this help:  python -c "from fileprovider import help; help()"

options:
  -h, --help       show this help message and exit
  --folder str     Folder to manage/store uploaded file(s) (default: /tmp/test)
  --mount str      Mount path, applied when ASGI deploy tool using (default: /mcp/)
  --transport str  MCP Transport Layer, applied when ASGI deploy tool using. (default: streamable-http)

# show helps for fastmcp run command:
fastmcp run -h
```


## Sample MCP Client

- source: src/clients/llmclient.py

```bash
cat ./examples/conf-mcpServers/test-servers.yaml | sed 's/transport: streamable-http/transport: streamable_http/g' | ./src/clients/llmclient.py
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
fastmcp run --server-spec src/gateways/mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8888 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir examples/openapi-specs  \
            -- -s ./examples/openapi-specs/ghec-get-org-pruned-openapi31-validated.json -b https://api.github.com

# boot MCP server with REST to MCP Gateway (with public and authorized spaces)
# Note this case has some security risk by proxying public/open <=> authorized space
#fastmcp run --server-spec src/gateways/mcp-gateway.py \
#           --transport streamable-http --host 0.0.0.0 --port 8888 --path /mcp/ -l DEBUG \
#           --reload --reload-dir src/gateways --reload-dir examples/openapi-specs  \
#           -- -s ./examples/openapi-specs/ghec-get-org-pruned-openapi31-validated.json -b https://api.github.com -a YOUR_GITHUB_PAT

# boot MCP server
fastmcp run --server-spec ./examples/src/mcpservers/echo.py  --transport http --host 0.0.0.0 --port 8890 --path /mcp/

# boot mashup server all-in-one, with MCP to MCP Gateway
fastmcp run --server-spec src/gateways/double-mcp-gateway.py \
            --transport streamable-http --host 0.0.0.0 --port 8889 --path /mcp/ -l DEBUG \
            --reload --reload-dir src/gateways --reload-dir ./examples/conf-mcpServers \
            -- -s ./examples/conf-mcpServers/test-servers.yaml

# test with client
cat ./examples/conf-mcpServers/test-servers.yaml  | sed 's/transport: streamable-http/transport: streamable_http/g' | ./src/clients/llmclient.py
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
