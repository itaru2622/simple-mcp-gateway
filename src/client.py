#!/usr/bin/env python3

# cf. https://github.com/jlowin/fastmcp/blob/main/docs/clients/client.mdx

#
#  MCP client to send request server in pure MCP
#   - get mcp server info to connect.
#   - send request to MCP server.
#

from fastmcp import FastMCP, Client
from typing import Any
import httpx
import yaml
import json
import argparse
import sys
import asyncio
import logging
from fastmcp.utilities.logging import get_logger
from collections import defaultdict
from fastapi.encoders import jsonable_encoder
from itertools import cycle
# my own ...
from utils import load


async def test(cli) -> Any:

    rtn = defaultdict(list[Any])
    arr = []

    cmds = [
             ( 'tools', cli.list_tools )
            ,( 'resources', cli.list_resources )
            ,( 'resource_templates', cli.list_resource_templates )
            ,( 'prompts', cli.list_prompts )
           ]

    async with cli:
      for k, op in cmds:
        tmp = await op()
        arr += zip( cycle([k]), (tmp or []) ) # same as: arr += [ (k, v) for v in (tmp or []) ]
        rtn[k] = tmp

    return rtn, arr


def get_event_loop() -> Any:
    '''get async event loop '''

    #return asyncio.get_event_loop() # DeprecationWarning There is no current event loop

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--spec',      help='mcpServeers config to connect (json/yaml/text[url])', default='/dev/stdin')
    parser.add_argument('-d', '--log_level', help='MCP log level',                      default='DEBUG')
    opts = parser.parse_args()

    #for comp in [ 'fastmcp.experimental.utilities.openapi.director',
    #              'fastmcp.experimental.server.openapi.components',
    #              'fastmcp.experimental.server.openapi.server' ]:
    #    get_logger(comp).setLevel(logging.DEBUG)
    #
    #logging.basicConfig(level=logging.DEBUG) # Configure root logger

    spec = load(opts.spec)
    client = Client(spec)
    #exit(0)

    #asyncio.run( test(client) )
    loop = get_event_loop()
    _, tmp = loop.run_until_complete(asyncio.gather( test(client) ))[0]
    loop.close()

    # reshape responded data to make them easy to use.
    rtn = []
    for _,v in tmp:
       d = v.model_dump(); # base data: pydantic BaseModel dump
       T = type(v)
       d.update({  'type': T.__name__, 'class': f'{T.__module__}.{T.__qualname__}' }) # add type info
       rtn.append(d)

    print(json.dumps(rtn, ensure_ascii=False, indent=2), file=sys.stdout)
