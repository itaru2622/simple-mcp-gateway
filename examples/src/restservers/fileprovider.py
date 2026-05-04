from fastapi import FastAPI, File, UploadFile, Response, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated
import io
import sys
import pathlib
import base64

# myown
from mytypes import MyFormMultipartFriendly

"""
### install dependencies:

pip install fastapi[standard]


### to start

uvicorn fileprovider:app --host 0.0.0.0 --port 8892 --reload 
"""

dir=pathlib.Path('/tmp/test') # limit the folder to serve.
dir.mkdir(exist_ok=True)      # ensure folder exists

# --------------

app = FastAPI(title='upload/download test server')

@app.post('/uploadByMyModel', operation_id='uploadByMyModel')
def uploadByModel(file: MyFormMultipartFriendly = Body(..., description='file to upload')) -> dict:
    '''Upload the file from client to server, with Model.

    Args:
     - file(MyFormMultipartFriendly): target file to upload

    Returns:
    - dict: contains filename and its size
    '''

    # ensure putting the file into safe folder.
    f = dir / file.options.filename
    print(f'{file=}', file=sys.stderr)

    content = file.getRawValue()
    if file.options.contentType.startswith('text/'):
       f.write_text(content, encoding='utf-8')
    else:
       f.write_bytes(content)

    rtn = {'filename': file.options.filename, 'file_size': len(content)}
    print(f'{rtn=}', file=sys.stderr)
    return rtn

# cf. https://fastapi.tiangolo.com/tutorial/request-files/
@app.post('/uploadByForm', operation_id='uploadByForm')
async def uploadByForm(file: Annotated[UploadFile, File(..., description='file to upload')]) -> dict:
    '''Upload the file from client to server, with Form.

    Args:
     - file(File): target file to upload

    Returns:
    - dict: contains filename and its size
    '''

    # ensure putting the file into safe folder.
    f = dir / file.filename

    content = await file.read()
    f.write_bytes(content) 

    rtn = {'filename': file.filename, 'file_size': len(content)}
    print(f'{rtn=}', file=sys.stderr)
    return rtn


@app.get('/download', operation_id='download')
async def download(path: str=Query(..., description='file to download')):
    '''Download the file from server to client, as content-disposition attachment.

    Args:
     - path(str): file for download
    '''

    # ensure file in the safe folder
    f = dir / path

    if not f.exists():
       return JSONResponse(content={"notFound": path}, status_code=404)

    data = f.read_bytes() 
    return Response(data, media_type='application/octet-stream', headers={'Content-Disposition': f'attachment; filename={path}'})


@app.get('/list', operation_id='list', summary='List')
def lsFiles() -> list[str]:
    '''
    get list of files and folders which ready to serve.

    Returns:
     - list[str]: list of files and folders.
    '''

    # returns the list of files, folders in safe folder, excepts hidden files
    items = [item.name for item in dir.iterdir() if not item.name.startswith('.')]
    return sorted(items)

