#!/usr/bin/env python

from fastmcp import FastMCP
import pathlib
import os
import sys
import argparse

# --------------

mcp = FastMCP("FileProvider")

@mcp.tool
def listFiles(path: str='.') -> list[str]:
    '''
    return list of files and folders specified in by the path(folder).

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

@mcp.tool
def getFileContent(path: str ) -> str | bytes:
    '''
    returns content of file specified by the path.

    Args:
      - path(str): target file whose content wanted.

    Returns:
      str|bytes: content of requested file.
    '''

    # reject if requested file starts with '.'
    if  path.rsplit('/',1)[1].startswith('.'):
        return 'Error: Access denied.'
    # reject if requested file starts with '/'
    if  path.startswith('/'):
        return 'Error: Access denied.'

    # ensure the path is under the managed dir.
    f = (dir / path).resolve()
    binary = {'.png', '.jpg', 'jpeg', '.pdf', '.zip'}

    if not f.exists():
        return f'Error: File not found.'

    # TODO: binary detection, smarter.
    if f.suffix.lower() in binary:
        print(f'content=binary {f}')
        return f.read_bytes()
    else:
        print(f'content=string {f}')
        return f.read_text(encoding="utf-8")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder',    help='toplevel folder to manage',                 default='/tmp')
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

    kwargs = dict(transport=opts.transport, log_level=opts.log_level)
    if opts.transport not in ['stdio']:
        kwargs = { k : v  for k, v in vars(opts).items() if k in ['host', 'port', 'path', 'transport'] }
    print(f'{kwargs=}', file=sys.stderr)

    mcp.run(**kwargs)
