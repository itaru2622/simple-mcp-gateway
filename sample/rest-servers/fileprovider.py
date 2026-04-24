from fastapi import FastAPI, File, UploadFile, Response, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated
import io
import sys
import pathlib
import base64

"""
### install dependencies:

pip install fastapi[standard]


### to start

uvicorn fileprovider:app --host 0.0.0.0 --port 8892 --reload 
"""

dir=pathlib.Path('/tmp/test') # limit the folder to serve.
dir.mkdir(exist_ok=True)      # ensure folder exists

# --------------

class FormMultipartOption(BaseModel):
    '''Metadata of file, like REST form/multipart metadata'''

    filename: str=Field(description='filename with suffix, like any.jpg', examples=['any.jpg', 'any.txt'] )
    contentType: str=Field(description='Content-Type, like text/plain or image/jpg;base64.  ";base64" indicates it requires base64 decode to get original raw data.',
                           examples=[ 'image/jpg;base64', 'application/octet-stream;base64', 'text/plain'])


class FormMultipartFriendly(BaseModel):
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

    options: FormMultipartOption=Field(description='metadata of file, like form/multipart.')
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


app = FastAPI(title='upload/download test server')

@app.post('/uploadByModel', operation_id='uploadByModel')
def uploadByModel(file: FormMultipartFriendly = Body(..., description='file to upload')) -> dict:
    '''Upload the file from client to server, with Model.

    Args:
     - file(FormMultipartFriendly): target file to upload

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

