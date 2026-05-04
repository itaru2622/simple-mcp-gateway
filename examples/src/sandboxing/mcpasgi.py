#!/usr/bin/env python

"""
sandboxing/debugging:  FastMCP x ASGI x reload option.

FastMCP Echo Server    cf. https://github.com/jlowin/fastmcp/blob/main/examples/echo.py
x
mount mcp to FastAPI app  cf. https://github.com/PrefectHQ/fastmcp/blob/main/docs/deployment/http.mdx
x
option handling with pydantic-settings
x
start app with uvicorn/fastmcp run command

# to start:
#   case 1) fastmcp run command
mount=/mcp/ fastmcp run --server-spec ./examples/src/sandboxing/mcpasgi.py:mcp --transport http     --host 0.0.0.0 --port 8890 --path /mcp/ --reload --reload-dir ./examples/src/sandboxing

#   case 2) uvicorn (after mcp mounted on FastAPI)
FASTMCP_LOG_LEVEL=DEBUG transport=http mount=/mcp/ uvicorn examples.src.sandboxing.mcpasgi:app      --host 0.0.0.0 --port 8890              --reload --reload-dir ./examples/src/sandboxing

#   case 3) uvicorn (instance of  mcp.http_app() )
FASTMCP_LOG_LEVEL=DEBUG transport=http mount=/     uvicorn examples.src.sandboxing.mcpasgi:mcp4asgi --host 0.0.0.0 --port 8890              --reload --reload-dir ./examples/src/sandboxing


"""

from fastmcp import FastMCP
import logging
import sys
import os

# option handling
from   pydantic_settings import BaseSettings, SettingsConfigDict
from   pydantic import Field
from   fastmcp.settings import Settings  as FastmcpSettings # optional, fastmcp-scoped pydantic-settings
# for ASGI friendly
from   fastapi import FastAPI
# myown, for debug
from FullRelayMiddleware import FullRelayMiddleware

class Settings(BaseSettings):
    ''' Settings for the app.

        folder=/tmp/test2 fastcmp run this:mcp --host 0.0.0.0 --port 8888 --path=/mcp/ --transport streamable-http
        folder=/tmp/test2 mount=/mcp/ transport=streamable-http   uvicorn this:app --host 0.0.0.0 --port 8888

        to print this help: python -c "from fileprovider import help; help()"
    '''
    path: str   = Field('/mcp/',     description='Mount path, applied when ASGI deploy tool used', alias='mount') # avoid conflicts with env:PATH. use mount in env/shell, but path in app
    transport: str = Field('streamable-http', description='MCP Transport Layer, applied when ASGI deploy tool used.')

    model_config = SettingsConfigDict(extra='allow', env_file=os.getenv('APPENVFILE', '.env'), env_prefix=os.getenv('PREFIX_APPENV', ''), env_nested_delimiter="__")

def help():
    '''just print help'''

    from pydantic_settings import CliApp
    sys.argv = [sys.argv[0], "--help"]
    CliApp.run(Settings)

logging.basicConfig(level=logging.DEBUG) # Configure root logger

# get and parse options
opts = Settings()
print(f'{opts=}', file=sys.stderr)

#-------------------------------------------------------------------------------------

# Create server
mcp = FastMCP("Echo Server")
#mcp.add_middleware(FullRelayMiddleware()) # insight internal behavior.

@mcp.tool
def echo_tool(text: str) -> str:
    """Echo the input text"""
    return text


@mcp.resource("echo://static")
def echo_resource() -> str:
    return "Echo!"


@mcp.resource("echo://{text}")
def echo_template(text: str) -> str:
    """Echo the input text"""
    return f"Echo: {text}"


@mcp.prompt("echo")
def echo_prompt(text: str) -> str:
    return text

#-------------------------------------------------------------------------------------
mcp4asgi = mcp.http_app(path='/', transport=opts.transport)
app = FastAPI(title="FastAPI app for FastMCP/ASGI", lifespan=mcp4asgi.lifespan)
app.mount(opts.path, mcp4asgi)

