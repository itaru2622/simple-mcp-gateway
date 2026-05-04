#!/usr/bin/env python

"""

# to start

# case1) with fastmcp run command

folder=/tmp/test  \
fastmcp run --server-spec ./examples/src/mcpservers/fileprovider.py:mcp --transport http --host 0.0.0.0 --port 8890 --path /mcp/ -l DEBUG --reload

# case2) with uvicorn/ASGI tool

FASTMCP_LOG_LEVEL=DEBUG   PYTHONPATH=./:${PYTHONPATH} \
transport=streamable-http mount=/mcp/ \
folder=/tmp/test uvicorn  examples.src.mcpservers.fileprovider:app --host 0.0.0.0 --port 8890 --reload --reload-include './example/src/**.py' --reload-include './src/**.py'

"""

from   fastmcp import FastMCP
from   fastmcp.utilities.types import File
import base64
import mimetypes
import pathlib
import os
import sys
# option handling
from   pydantic_settings import BaseSettings, SettingsConfigDict
from   pydantic import Field
from   fastmcp.settings import Settings  as FastmcpSettings # optional, fastmcp-scoped pydantic-settings
# for ASGI friendly
from   fastapi import FastAPI

# myown
from   mytypes import MyFormMultipartFriendly


#--------------------
# app option handling is empowered by pydantic-settings, to make app independent from deployment tool.
#
# deployment tools  | unit for watch/reload | app option handling
# ------------------+-----------------------+-----------------------------------------------------
# FastMCP run cmd   | reload-dir ONLY       | pydantic-settings + argparse (after double-dash ' -- ')
# uvicorn           | + reload-[in|ex]clude | pydantic-settings ONLY
# other ASGI tool   | same as uvicorn     =====>
#
# i.e: when app option is empowered by pydantic-settings, any can deploy the app as described aboves.
#

class Settings(BaseSettings):
    ''' Settings for the app.

        NG:  use commandline options.
        OK:  compatible with env style, like below:

        folder=/tmp/test2 fastcmp run this:mcp --host 0.0.0.0 --port 8888 --path=/mcp/ --transport streamable-http
        folder=/tmp/test2 mount=/mcp/ transport=streamable-http   uvicorn this:app --host 0.0.0.0 --port 8888

        to print this help: python -c "from fileprovider import help; help()"
    '''
    folder: str = Field('/tmp/test', description='Folder to manage/store uploaded file(s)')
    path: str   = Field('/mcp/',     description='Mount path, applied when ASGI deploy tool used', alias='mount') # avoid conflicts with env:PATH. use mount in env/shell, but path in app
    transport: str = Field('streamable-http', description='MCP Transport Layer, applied when ASGI deploy tool used.')
    # fastmcp: FastmcpSettings|None = Field({}, description='FastMCP Config detected via fastmcp-scoped env vars') # valid only if fastmcp scoped envs are used.

    # tune config: extras:notFORBITTEN, .env and env_prefix. those are tunable via envs of APPENVFILE, and PREFIX_APPENV
    model_config = SettingsConfigDict(extra='allow', env_file=os.getenv('APPENVFILE', '.env'), env_prefix=os.getenv('PREFIX_APPENV', ''), env_nested_delimiter="__")
    # NOTE https://pydantic.dev/docs/validation/latest/concepts/pydantic_settings/#command-line-support doesn't work with ASGI/fastmcp


# get and parse options
opts = Settings()
print(f'{opts=}', file=sys.stderr)
#----------------------

# prepare folder to manager uploaded files.
dir = pathlib.Path(opts.folder).resolve()
dir.mkdir(exist_ok=True)

#--------------------

mcp = FastMCP("FileProvider")

# empowering deployment by ASGI/FastAPI
#  - https://github.com/PrefectHQ/fastmcp/blob/main/docs/deployment/http.mdx
#  - https://github.com/PrefectHQ/fastmcp/blob/main/docs/integrations/fastapi.mdx

mcp4asgi = mcp.http_app(path='/', transport=opts.transport)
app = FastAPI(title="FastAPI app for FastMCP/ASGI", lifespan=mcp4asgi.lifespan)
app.mount(opts.path, mcp4asgi)

# ready to deploy, with tools:
# - NOTE: uppercase words has to be managed by deployment tool, by env vars in tool-scope or commandline options
#
# fastmcp run ...:mcp       => http://HOST:PORT/MOUNT
# uvicorn     ...:app       => http://HOST:PORT/mcp/  //  mount=/mcp/          transport=streamable-http
# uvicorn     ...:mcp4asgi  => http://HOST:PORT/      //  mcp.http_app(path=/) transport=streamable-http


# definitions of MCP tool -------------------

@mcp.tool
def lsFiles(path: str='.') -> list[str]:
    '''
    get list of files and folders specified by the path(folder).

    Args:
     - path(str) target path to get list of the files and folders.

    Returns:
     - list[str]: list of files and folders.
    '''

    # ensure the path is under the managed folder.
    d = (dir / path ).resolve()

    if not d.exists() or not d.is_dir():
        return [f'Error: not found/folder']


    # returns the list of files, folders excepts hidden files
    items = [item.name for item in d.iterdir() if not item.name.startswith('.')]
    return sorted(items)

# cf. https://github.com/PrefectHQ/fastmcp/blob/main/examples/get_file.py
@mcp.tool()
async def getFile2(path: str) -> File:
        '''
        get file from the server by the path in FORM style.

        Args:
        - path(str): file path to get.

        Returns:
        - File: instance of fastmcp.utilities.types.File
        '''

        # reject if requested file starts with '.'
        if  '/' in path and path.rsplit('/',1)[1].startswith('.'):
            return 'Error: Access denied.'

        # reject if requested path starts with '/' or '.'
        if  path.startswith(('/', '.')):
            return 'Error: Access denied.'

        # ensure the file is under the managed dir.
        f = (dir / path).resolve()
        if not f.exists():
            return f'Error: File not found.'

        return File(path=f)


@mcp.tool
def getFile(path: str ) -> str | MyFormMultipartFriendly:
    '''
    get file content specified by the path in MyFormMultipartFriendly.

    Args:
      - path(str): target file whose content wanted.

    Returns:
      str|MyFormMultipartFriendly: content of file(str or binary in json+base64 encoded).
    '''

    # reject if requested file starts with '.'
    if  '/' in path and path.rsplit('/',1)[1].startswith('.'):
        return 'Error: Access denied.'

    # reject if requested path starts with '/' or '.'
    if  path.startswith(('/', '.')):
        return 'Error: Access denied.'

    # ensure the file is under the managed dir.
    f = (dir / path).resolve()
    if not f.exists():
        return f'Error: File not found.'

    # TODO: text/binary mimetype detection, smarter with python-magic magic.Magic(mime=True)
    mime = mimetypes.guess_type(f)[0] or 'application/octet-stream'

    if mime.startswith('text/'):
        print(f'content=text {f}', file=sys.stderr)
        return f.read_text(encoding='utf-8')

    print(f'content=binary {f}', file=sys.stderr)
    body = f.read_bytes()
    blob = base64.b64encode( body  ).decode("utf-8")
    mime += ';base64'
    rtn = MyFormMultipartFriendly(value=blob, options=dict(filename=path, contentType=mime))
    print(f'{len(rtn.getRawValue())=}', file=sys.stderr)
    return rtn

    """
    alternative to MyFormMultipartFriendly
    from mcp.types import EmbeddedResource, BlobResourceContents
    return EmbeddedResource(type='resource', resource=BlobResourceContents(uri=f'file:///{path}', mimeType=mime, blob=blob) )
    """

def help():
    '''just print help'''

    from pydantic_settings import CliApp
    sys.argv = [sys.argv[0], "--help"]
    CliApp.run(Settings)
