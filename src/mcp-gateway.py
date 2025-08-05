#!/usr/bin/env python3

# cf. https://github.com/jlowin/fastmcp/blob/main/docs/integrations/openapi.mdx
# cf. https://qiita.com/__Kat__/items/8e0144c19aa3079f1b6b

#
#  trying to gateway from existing REST server for User/AI/LLM with:
#   - load openAPI spec file,
#   - generate MCP server for AI/LLM for the above spec.
#   - message forwarding among User/AI/LLM <=> MCP <=> existing REST server.
#

from fastmcp import FastMCP
from fastmcp.server.openapi import ( FastMCPOpenAPI, RouteMap, MCPType,)
from fastmcp.experimental.server.openapi import RouteMap, MCPType
from typing import Any
import httpx
import yaml
import json
import argparse
import sys
import asyncio
import logging
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.utilities.logging import get_logger
from FullRelayMiddleware import FullRelayMiddleware


def load(path:str='/dev/stdin') -> Any:
    """load json/yaml from file"""

    with open(path, "r", encoding='utf-8') as fp:
        c = fp.read()
        try: # try json first
            d = json.loads(c)
        except: # if failed, try yaml
            d = yaml.safe_load(c)
        return d

async def test(cli, uri) -> Any:
    rtn = await cli.get(uri)
    rtn = rtn.json()
    rtn = json.dumps(rtn, indent=2, ensure_ascii=False)
    print(f'{rtn}', file=sys.stderr)


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--spec',      help='OpenAPI spec file for gateway (json/yaml)', default='/dev/stdin')
    parser.add_argument('-b', '--baseURL',   help='baseURL to REST Server',                    default='')
    parser.add_argument('-a', '--token',     help='bearer token to REST server',               default=None)
    parser.add_argument('-t', '--transport', help='MCP server transport',                      default='http')
    parser.add_argument('-p', '--port',      help='MCP server port',                           default=8888)
    parser.add_argument('-H', '--host',      help='MCP server host to listen',                 default='0.0.0.0')
    parser.add_argument('-l', '--path',      help='MCP server path to bind',                   default='/mcp')
    parser.add_argument('-d', '--log_level', help='MCP server log level',                      default='DEBUG')
    opts = parser.parse_args()

    opts.headers = {}

    if opts.token not in [None, '']:
         opts.headers.update(Authorization=f'Bearer {opts.token}')
    print(f"opts: ########### {opts}", file=sys.stderr)

    #exit(0)

    for comp in [ "fastmcp.experimental.utilities.openapi.director",
                  "fastmcp.experimental.server.openapi.components",
                  "fastmcp.experimental.server.openapi.server",
                  "FullRelayMiddleware"]:
        get_logger(comp).setLevel(logging.DEBUG)

    #logging.basicConfig(level=logging.DEBUG) # Configure root logger
    
    spec = load(opts.spec)

    # cli to access REST Server.
    cli = httpx.AsyncClient(base_url=opts.baseURL, headers=opts.headers ) # cli to REST Server.

    #asyncio.run( test( cli, "/orgs/..."))
    #exit(0)

    route_maps = [
       RouteMap(methods=["GET"], pattern=r".*\{.*\}.*", mcp_type=MCPType.RESOURCE_TEMPLATE),
       RouteMap(methods=["GET"], pattern=r".*",         mcp_type=MCPType.RESOURCE),
#      RouteMap(mcp_type=MCPType.TOOL),
    ]

    mcp = FastMCP.from_openapi(spec, client=cli, route_maps=route_maps)


    mcp.add_middleware(FullRelayMiddleware())
    '''
    logger = get_logger('fastmcp.server.middleware.logging.LoggingMiddleware')
    logger.setLevel(logging.DEBUG)
    mcp.add_middleware(LoggingMiddleware(logger=logger, log_level=logging.DEBUG))
    '''

    kwargs = dict(transport=opts.transport)
    if opts.transport not in ['stdio']:
        kwargs = { k : v  for k, v in vars(opts).items() if k in ['host', 'port', 'path', 'transport', 'log_level' ] }

    print(f"{kwargs=}", file=sys.stderr)
    mcp.run(**kwargs)
