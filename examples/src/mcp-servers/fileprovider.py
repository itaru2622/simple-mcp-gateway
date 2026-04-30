#!/usr/bin/env python

"""

# to start, fastmmcp run [any options of fastmcp] --(double dash) [options for server] like below:
fastmcp run --server-spec ./examples/src/mcp-servers/fileprovider.py --transport http --host 0.0.0.0 --port 8890 --path /mcp/ -l debug --reload --  --folder /tmp/test

"""

from fastmcp import FastMCP
from fastmcp.utilities.types import File

import base64
import mimetypes
import pathlib
import os
import sys
import argparse

# myown
from mytypes import MyFormMultipartFriendly

#--------------------
# option handling

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--folder',    help='toplevel folder to serve',                  default='/tmp')
opts = parser.parse_args()

print(f'{opts=}', file=sys.stderr)
#exit(0)

dir = pathlib.Path(opts.folder).resolve()
dir.mkdir(exist_ok=True)

#--------------------

mcp = FastMCP("FileProvider")

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

"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder',    help='toplevel folder to serve',                  default='/tmp/test')
    parser.add_argument('-t', '--transport', help='MCP server transport',                      default='http')
    parser.add_argument('-p', '--port',      help='MCP server port',  type=int,                default=8890)
    parser.add_argument('-H', '--host',      help='MCP server host to listen',                 default='0.0.0.0')
    parser.add_argument('-l', '--path',      help='MCP server path to bind',                   default='/mcp/')
    parser.add_argument('-d', '--log_level', help='MCP server log level',                      default='DEBUG')
    opts = parser.parse_args()

    print(f'{opts=}', file=sys.stderr)
    #exit(0)

    dir = pathlib.Path(opts.folder).resolve()
    dir.mkdir(exist_ok=True)

    kwargs = { k : v  for k, v in vars(opts).items() if k in ['transport', 'log_level'] }
    if opts.transport not in ['stdio']:
        kwargs.update( { k : v  for k, v in vars(opts).items() if k in ['host', 'port', 'path']} )
    print(f'{kwargs=}', file=sys.stderr)

    mcp.run(**kwargs)
"""
