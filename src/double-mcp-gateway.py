#!/usr/bin/env python3

# cf. https://github.com/jlowin/fastmcp/blob/main/docs/servers/proxy.mdx
#     https://github.com/jlowin/fastmcp/blob/main/docs/servers/proxy.mdx#multi-server-configurations
#
# This gateway aims to be the man in the middle among AI/LLM and existing MCP server,
# to apply some control on the communication, like enterprise HTTP security gateway.
#
# trying to gateway from existing MCP server for User/AI/LLM with:
#   - load MCP server config for existing backend MCP server(s) with HTTP transport(i.e. Streamable HTTP)
#   - generate MCP server for AI/LLM as man in the middle.
#   - message forwarding among User/AI/LLM <=> MCP <=> existing MCP server.
#
#  note: original fastMCP supports backend MCP server with stdio transport, but this gateway doesn't support it yet.
#

from fastmcp import FastMCP
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

# my own ...
from FullRelayMiddleware import FullRelayMiddleware
from utils.conf import load


async def test(cli, uri) -> Any:
    rtn = await cli.get(uri)
    rtn = rtn.json()
    rtn = json.dumps(rtn, indent=2, ensure_ascii=False)
    print(f'{rtn}', file=sys.stderr)


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--spec',      help='backend MCP server config (json|yaml|url)', default='/dev/stdin')
    parser.add_argument('-t', '--transport', help='MCP server transport',                      default='http')
    parser.add_argument('-p', '--port',      help='MCP server port',                           default=8889)
    parser.add_argument('-H', '--host',      help='MCP server host to listen',                 default='0.0.0.0')
    parser.add_argument('-l', '--path',      help='MCP server path to bind',                   default='/mcp')
    parser.add_argument('-d', '--log_level', help='MCP server log level',                      default='DEBUG')
    opts = parser.parse_args()

    spec = load(opts.spec)
    # exit(0)

    for comp in [ "fastmcp.experimental.utilities.openapi.director",
                  "fastmcp.experimental.server.openapi.components",
                  "fastmcp.experimental.server.openapi.server",
                  "fastmcp.resources.resource_manager",
                  "fastmcp.utilities.components",
                  "FullRelayMiddleware"]:
        get_logger(comp).setLevel(logging.DEBUG)

    #logging.basicConfig(level=logging.DEBUG) # Configure root logger

    mcp = FastMCP.as_proxy(backend=spec, name='MCP to MCP gateway') # create instance as MCP<=>MCP proxy.
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
    mcp.run(**kwargs) # run instance.
