# Files

Types:

```python
from witan.types import (
    FileRetrieveResponse,
    FileListResponse,
    FileDeleteResponse,
    FileUploadResponse,
)
```

Methods:

- <code title="get /v0/files/{fileId}">client.files.<a href="./src/witan/resources/files.py">retrieve</a>(file_id) -> <a href="./src/witan/types/file_retrieve_response.py">FileRetrieveResponse</a></code>
- <code title="get /v0/files">client.files.<a href="./src/witan/resources/files.py">list</a>(\*\*<a href="src/witan/types/file_list_params.py">params</a>) -> <a href="./src/witan/types/file_list_response.py">SyncCursor[FileListResponse]</a></code>
- <code title="delete /v0/files/{fileId}">client.files.<a href="./src/witan/resources/files.py">delete</a>(file_id) -> <a href="./src/witan/types/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /v0/files/{fileId}/content">client.files.<a href="./src/witan/resources/files.py">get_content</a>(file_id) -> BinaryAPIResponse</code>
- <code title="post /v0/files">client.files.<a href="./src/witan/resources/files.py">upload</a>(\*\*<a href="src/witan/types/file_upload_params.py">params</a>) -> <a href="./src/witan/types/file_upload_response.py">FileUploadResponse</a></code>

# Responses

Types:

```python
from witan.types import ResponseCreateResponse
```

Methods:

- <code title="post /v0/responses">client.responses.<a href="./src/witan/resources/responses.py">create</a>(\*\*<a href="src/witan/types/response_create_params.py">params</a>) -> <a href="./src/witan/types/response_create_response.py">ResponseCreateResponse</a></code>
