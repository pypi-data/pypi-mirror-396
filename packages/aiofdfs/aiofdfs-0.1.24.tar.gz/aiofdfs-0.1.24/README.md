# Async FastDFS Client Usage Guide

This project implements **asynchronous file upload and download** for FastDFS.

This document explains how to use `Async_Fdfs_Client` to perform **local file upload/download and FastAPI-based upload/download**.

First install dependencies:

```bash
pip install aiofdfs
```

# 1. Uploading and Downloading Local Files

In a pure script environment, you can directly use the asynchronous methods provided by `Async_Fdfs_Client` to upload and download files from FastDFS.
First, initialize the configuration:

```python
from aiofdfs import FastDfsConf

def get_fdfs_conf():
    return FastDfsConf(
        tracker_servers=['192.168.0.50:22122'],
        connect_timeout=3,
        network_timeout=3,
        # The index of the storage directory. If not set or set to -1, no control is applied.
        # If set to a value >= 0, the upload directory is strictly controlled.
        store_path_index=1
    )
```

The following example demonstrates local file upload and download using unit tests.

## 1.1. File Upload

```python
@pytest.mark.asyncio
async def test_upload_file():
    conf = get_fdfs_conf()
    async with Async_Fdfs_Client(conf) as fdfs_client:
        # Local file to upload
        local_file = 'E:/demo.zip'
        ret = await fdfs_client.upload_by_filename(local_file)
        print(ret)
```

Example response:

```json
{
  "group_name": "group1",
  "file_id": "group1/M01/00/00/xxxxxx.zip",
  "file_name": "demo.zip",
  "file_size": "20MB",
  "storage_ip": "192.168.0.50"
}
```

## 1.2. File Download

```python
@pytest.mark.asyncio
async def test_download_file():
    conf = get_fdfs_conf()
    async with Async_Fdfs_Client(conf) as fdfs_client:
        # Path to save the downloaded file
        local_file_name = 'E:/demo.zip'
        remote_file_id = 'group1/M01/00/00/xxxxxx.zip'
        ret = await fdfs_client.download_to_file(local_file_name, remote_file_id)
        print(ret)
```

Example output:

```bash
{
    'file_id': 'group1/M01/00/00/xxxxxx.zip',
    # Local file path
    'content': 'E:/demo.zip',
    'download_size': '20MB',
    'storage_ip': b'192.168.0.50'
}
```

# 2. Integrating with FastAPI for Upload and Download

This section provides APIs that are closer to real-world business scenarios and can be used directly in service applications.

Initialize the client:

```python
from aiofdfs import FastDfsConf, Async_Fdfs_Client

def get_fdfs_conf():
    return FastDfsConf(
        tracker_servers=['192.168.0.50:22122'],
        connect_timeout=3,
        network_timeout=3,
        # The index of the storage directory. If not set or set to -1, no control is applied.
        # If set to a value >= 0, the upload directory is strictly controlled.
        store_path_index=1
    )

# Initialize client
fdfs_client = Async_Fdfs_Client(get_fdfs_conf())
```

## 2.1. File Upload API

```python
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    result = await fdfs_client.upload_by_upload_file(file)
    return result
```

Example response:

```json
{
  "group_name": "group1",
  "file_id": "group1/M01/00/04/xxxxxx.pdf",
  "file_name": "example.pdf",
  "file_size": "100KB",
  "storage_ip": "192.168.0.50"
}
```

## 2.2. File Download API

```python
from urllib.parse import quote

@app.get("/download")
async def download(file_id: str):
    meta_data = await fdfs_client.get_meta_data(file_id)
    file_name = meta_data.get("OriginFileName")
    file_size = meta_data.get("OriginFileSize")

    quoted_filename = quote(file_name)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_filename}",
        "Content-Length": str(file_size)
    }

    return StreamingResponse(
        fdfs_client.download_to_generator(file_id),
        headers=headers,
        media_type="application/octet-stream"
    )
```

This allows the browser or client to download the file directly.

# 3. REST Client Test Script (VSCode)

The VS Code REST Client extension can be used to quickly test the API.

## 3.1. File Upload

```bash
###
POST http://localhost:8000/upload
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="example.pdf"
Content-Type: application/pdf

< E:\demo\example.pdf
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="json_data"

{
  "demo": "hello"
}
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

## 3.2. File Download

```bash
###
GET http://localhost:8000/download?file_id=group1/M01/00/04/xxxxxx.pdf
```
