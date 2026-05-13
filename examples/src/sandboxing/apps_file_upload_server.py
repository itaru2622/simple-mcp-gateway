'''
#
# cf. https://github.com/PrefectHQ/fastmcp/blob/main/examples/apps/file_upload/file_upload_server.py
# MCP Apps for file upload, to test how to support binary file uploading from user-side AI/LLM.
#
'''

from fastmcp import FastMCP
from fastmcp.apps.file_upload import FileUpload
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI

class MyFileUpload(FileUpload):
   def _get_scope_key(self, ctx: Context) -> str:
        '''Return the key used to partition file storage.'''
        # no partition for testing
        return '__default__'

mcp = FastMCP('File Upload Server')
mcp.add_provider( MyFileUpload() )

mcp4asgi = mcp.http_app(path='/', transport='sse')

app = FastAPI(title='FastAPI app for FastMCP/ASGI', lifespan=mcp4asgi.lifespan)
app.mount('/sse', mcp4asgi)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)

'''
# start:
# - case 1) fastmcp cmd with mcp instance:
fastmcp dev apps ./apps_file_upload_server.py --host 0.0.0.0 --mcp-port XXXX --dev-port YYYY

# - case 2) uvicorn/ASGI with app instance:
uvicorn apps_file_upload_server:app --host 0.0.0.0 --port XXXX
'''
