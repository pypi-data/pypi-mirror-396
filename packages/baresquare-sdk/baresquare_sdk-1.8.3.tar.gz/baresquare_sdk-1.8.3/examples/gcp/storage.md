# Google Cloud Storage Examples

This document provides examples of how to use the `Storage` class for Google Cloud Storage operations.

## Authentication

Check the authentication.md for more details

```python
from baresquare_sdk.gcp.storage import Storage
from baresquare_sdk.gcp.authentication import GoogleAuth

# Initialize storage client
storage_client = Storage(GoogleAuth())
```

## Basic Operations

### Upload a File

```python
# Upload a local file
storage_client.upload_file(
    bucket_name="my-bucket",
    blob_name="path/to/file.txt",
    file_path="local_file.txt",
    content_type="text/plain",
    metadata={"author": "user", "version": "1.0"}
)
```

### Upload Bytes Data

```python
# Upload bytes data directly
data = b"Hello, World!"
storage_client.upload_bytes(
    bucket_name="my-bucket",
    blob_name="data/hello.txt",
    data=data,
    content_type="text/plain"
)
```

### Upload DataFrames

```python
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['New York', 'London', 'Tokyo']
})

# Upload as CSV
storage_client.upload_data(
    bucket_name="my-bucket",
    blob_name="data/users.csv",
    data=df,
    format="csv",
    metadata={"source": "user_export", "version": "1.0"}
)
```

`upload_data` also supports `word` format

### Download a File

```python
# Download to a local file
storage_client.download_file(
    bucket_name="my-bucket",
    blob_name="path/to/file.txt",
    destination_path="downloaded_file.txt"
)
```

### Download as Bytes

```python
# Download blob content as bytes
data = storage_client.download_bytes(
    bucket_name="my-bucket",
    blob_name="path/to/file.txt"
)
print(data.decode('utf-8'))
```

### Download as Bytes and convert to pandas

```python
# Download blob content as bytes
data = storage_client.download_bytes(
    bucket_name="my-bucket",
    blob_name="path/to/file.csv"
)
df = pd.read_csv(io.BytesIO(data))
print(df.head())
```

### Check if Blob Exists

```python
# Check if a blob exists
exists = storage_client.exists("my-bucket", "path/to/file.txt")
if exists:
    print("File exists!")
```

### Delete a Blob

```python
# Delete a blob
storage_client.delete_blob("my-bucket", "path/to/file.txt")
```

### List Blobs

```python
# List all blobs in a bucket
blobs = storage_client.list_blobs("my-bucket")
for blob in blobs:
    print(f"Blob: {blob.name}, Size: {blob.size}")

# List blobs with prefix
blobs = storage_client.list_blobs("my-bucket", prefix="data/")
for blob in blobs:
    print(f"Blob: {blob.name}")
```
