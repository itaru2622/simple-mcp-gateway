from pydantic import BaseModel, Field
import base64


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
