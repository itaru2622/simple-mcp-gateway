#!/usr/bin/env python

from fastmcp import FastMCP
from fastmcp.utilities.types import File

import base64
import mimetypes
import pathlib
import os
import sys
import argparse
from pydantic import BaseModel, Field

# --------------

class MyFormMultipartOption(BaseModel):
    '''Metadata of file, like REST form/multipart metadata'''

    filename: str=Field(description='filename with suffix, like any.jpg', examples=['any.jpg', 'any.txt'] )
    contentType: str=Field(description='Content-Type, like text/plain or image/jpg;base64.  ";base64" indicates it requires base64 decode to get original raw data.',
                           examples=[ 'image/jpg;base64', 'application/octet-stream;base64', 'text/plain'])


class MyFormMultipartFriendly(BaseModel):
    '''REST form/multipart friendly class for MCP.

    MCP considerations:
    - MCP is based on JSON-RPC, so it CANNOT transfer binary as it is.
    - to transfer binary in MCP, it requires base64 encode/decode for send/receive.
    - to create the instance for binary file, add ';base64' in options.contentType as suffix and value needs to be base64 encoded.
    - to get raw data from this instance, it requires base64 decode in case of binary, use getRawValue member function for instance.

    JSON parser considerations:
    - if control character exists, it raises runtime error.
    - when uploading binary in base64 encoded text, encoded text should not have any control charactor, includeing NR CL. as described above.

    '''

    options: MyFormMultipartOption=Field(description='metadata of file, like form/multipart.')
    value: str=Field(description='''content of file in string.
                                    NOTE: any control charactor caused runtime error, even base64 encoded string.
                                    When uploading binary, remove all newline from result of base64 encode.
                                    in short, ```cat img.jpg | base64 | tr -d '[:cntrl:]'```
                                 ''')

    def getRawValue(self) -> str|bytes:
        '''get the raw value according to the options.contentType.

        Returns:
        - str|bytes: raw data of value.
        '''

        # base64 encoded
        if self.options.contentType.endswith(';base64'):
            return base64.b64decode(self.value)

        # other cases, text/*, or no ';base64' in contentType
        return self.value
#---

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

        return File(path=path)


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
    if  path.rsplit('/',1)[1].startswith('.'):
        return 'Error: Access denied.'

    # reject if requested file starts with '/'
    if  path.startswith('/'):
        return 'Error: Access denied.'

    # ensure the path is under the managed dir.
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder',    help='toplevel folder to serve',                  default='/tmp')
    parser.add_argument('-t', '--transport', help='MCP server transport',                      default='http')
    parser.add_argument('-p', '--port',      help='MCP server port',  type=int,                default=8890)
    parser.add_argument('-H', '--host',      help='MCP server host to listen',                 default='0.0.0.0')
    parser.add_argument('-l', '--path',      help='MCP server path to bind',                   default='/mcp')
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
