import io
from pathlib import Path
from typing import BinaryIO, Union

import pandas as pd
from google.cloud import storage
from google.cloud.storage import Blob, Bucket

from baresquare_sdk.gcp.authentication import CredentialProvider, GoogleAuth
from baresquare_sdk.gcp.clients import GCPClients


class Storage:
    """Google Cloud Storage client for uploading and downloading files.

    This class provides a simple interface for common Google Cloud Storage operations
    including uploading files, downloading files, and managing blobs.
    """

    _SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    def __init__(self, source: CredentialProvider | GCPClients, quota_project: str | None = None):
        """Initialize the Storage client.

        Args:
            source: Either a CredentialProvider or GCPClients instance.
            quota_project: Optional project ID for quota tracking.
        """
        if isinstance(source, GCPClients):
            self._client: storage.Client = source.storage()
            return

        cred_provider = source if isinstance(source, CredentialProvider) else GoogleAuth()
        credentials = cred_provider.get_credentials(self._SCOPES)

        final_quota_project = quota_project
        if not final_quota_project and hasattr(credentials, "project_id") and credentials.project_id:
            final_quota_project = credentials.project_id

        self._client: storage.Client = storage.Client(credentials=credentials, project=final_quota_project)

    def get_bucket(self, bucket_name: str) -> Bucket:
        """Get a bucket by name.

        Args:
            bucket_name: The name of the bucket.

        Returns:
            A Bucket object.
        """
        return self._client.bucket(bucket_name)

    def get_blob(self, bucket_name: str, blob_name: str) -> Blob:
        """Get a blob by bucket and blob name.

        Args:
            bucket_name: The name of the bucket.
            blob_name: The name of the blob.

        Returns:
            A Blob object.
        """
        bucket = self.get_bucket(bucket_name)
        return bucket.blob(blob_name)

    def prepare_data(self, data, format: str, **kwargs) -> tuple[io.BytesIO, str]:
        file_buffer = io.BytesIO()
        content_type = None
        # Check the file extension to determine the type
        if format == "word":
            # Save the Word document to the buffer
            data.save(file_buffer)
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif format == "csv":
            # Save the CSV to the buffer
            data.to_csv(file_buffer, index=False)
            content_type = "text/csv"
        else:
            raise ValueError(f"Unsupported file type: {format}")

        return file_buffer, content_type

    def upload_file(
        self,
        bucket_name: str,
        blob_name: str,
        file_path: Union[str, Path],
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Blob:
        """Upload a file to Google Cloud Storage.

        Args:
            bucket_name: The name of the bucket to upload to.
            blob_name: The name of the blob in the bucket.
            file_path: Path to the file to upload.
            content_type: Optional MIME type of the file.
            metadata: Optional metadata to attach to the blob.

        Returns:
            The uploaded Blob object.
        """
        blob = self.get_blob(bucket_name, blob_name)

        if content_type:
            blob.content_type = content_type

        if metadata:
            blob.metadata = metadata

        blob.upload_from_filename(str(file_path))
        return blob

    def upload_bytes(
        self,
        bucket_name: str,
        blob_name: str,
        data: bytes,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Blob:
        """Upload bytes data to Google Cloud Storage.

        Args:
            bucket_name: The name of the bucket to upload to.
            blob_name: The name of the blob in the bucket.
            data: The bytes data to upload.
            content_type: Optional MIME type of the data.
            metadata: Optional metadata to attach to the blob.

        Returns:
            The uploaded Blob object.
        """
        blob = self.get_blob(bucket_name, blob_name)

        if content_type:
            blob.content_type = content_type

        if metadata:
            blob.metadata = metadata

        blob.upload_from_string(data)
        return blob

    def upload_file_obj(
        self,
        bucket_name: str,
        blob_name: str,
        file_obj: BinaryIO,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Blob:
        """Upload a file-like object to Google Cloud Storage.

        Args:
            bucket_name: The name of the bucket to upload to.
            blob_name: The name of the blob in the bucket.
            file_obj: A file-like object to upload.
            content_type: Optional MIME type of the file.
            metadata: Optional metadata to attach to the blob.

        Returns:
            The uploaded Blob object.
        """
        blob = self.get_blob(bucket_name, blob_name)

        if content_type:
            blob.content_type = content_type

        if metadata:
            blob.metadata = metadata

        blob.upload_from_file(file_obj)
        return blob

    def download_file(
        self,
        bucket_name: str,
        blob_name: str,
        destination_path: Union[str, Path],
    ) -> None:
        """Download a file from Google Cloud Storage.

        Args:
            bucket_name: The name of the bucket to download from.
            blob_name: The name of the blob to download.
            destination_path: Local path where the file should be saved.
        """
        blob = self.get_blob(bucket_name, blob_name)
        blob.download_to_filename(str(destination_path))

    def download_bytes(self, bucket_name: str, blob_name: str) -> bytes:
        """Download a blob as bytes from Google Cloud Storage.

        Args:
            bucket_name: The name of the bucket to download from.
            blob_name: The name of the blob to download.

        Returns:
            The blob content as bytes.
        """
        blob = self.get_blob(bucket_name, blob_name)
        return blob.download_as_bytes()

    def download_to_file_obj(
        self,
        bucket_name: str,
        blob_name: str,
        file_obj: BinaryIO,
    ) -> None:
        """Download a blob to a file-like object.

        Args:
            bucket_name: The name of the bucket to download from.
            blob_name: The name of the blob to download.
            file_obj: A file-like object to write the data to.
        """
        blob = self.get_blob(bucket_name, blob_name)
        blob.download_to_file(file_obj)

    def exists(self, bucket_name: str, blob_name: str) -> bool:
        """Check if a blob exists in the bucket.

        Args:
            bucket_name: The name of the bucket.
            blob_name: The name of the blob.

        Returns:
            True if the blob exists, False otherwise.
        """
        blob = self.get_blob(bucket_name, blob_name)
        return blob.exists()

    def delete_blob(self, bucket_name: str, blob_name: str) -> None:
        """Delete a blob from Google Cloud Storage.

        Args:
            bucket_name: The name of the bucket.
            blob_name: The name of the blob to delete.
        """
        blob = self.get_blob(bucket_name, blob_name)
        blob.delete()

    def list_blobs(
        self,
        bucket_name: str,
        prefix: str | None = None,
        delimiter: str | None = None,
        max_results: int | None = None,
    ) -> list[Blob]:
        """List blobs in a bucket.

        Args:
            bucket_name: The name of the bucket.
            prefix: Optional prefix to filter blobs.
            delimiter: Optional delimiter for grouping.
            max_results: Optional maximum number of results to return.

        Returns:
            A list of Blob objects.
        """
        bucket = self.get_bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter, max_results=max_results)
        return list(blobs)

    def upload_string(
        self,
        bucket_name: str,
        blob_name: str,
        data: str,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
        encoding: str = "utf-8",
    ) -> Blob:
        """Upload a string to Google Cloud Storage.

        Args:
            bucket_name: The name of the bucket to upload to.
            blob_name: The name of the blob in the bucket.
            data: The string data to upload.
            content_type: Optional MIME type of the data.
            metadata: Optional metadata to attach to the blob.
            encoding: Text encoding to use (default: utf-8).

        Returns:
            The uploaded Blob object.
        """
        return self.upload_bytes(
            bucket_name=bucket_name,
            blob_name=blob_name,
            data=data.encode(encoding),
            content_type=content_type or "text/plain",
            metadata=metadata,
        )

    def upload_data(
        self,
        bucket_name: str,
        blob_name: str,
        data: pd.DataFrame,
        format: str = "csv",
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
        **kwargs,
    ) -> Blob:
        """Upload data to Google Cloud Storage in various formats.

        Args:
            bucket_name: The name of the bucket to upload to.
            blob_name: The name of the blob in the bucket.
            data: The data to upload (pandas DataFrame).
            format: Output format ('csv', 'parquet', 'json', 'excel', 'word').
            content_type: Optional MIME type of the data.
            metadata: Optional metadata to attach to the blob.
            **kwargs: Additional arguments passed to pandas to_* methods.

        Returns:
            The uploaded Blob object.

        Raises:
            ValueError: If format is not supported.
        """
        # Create a buffer to hold the file content
        file_buffer, content_type = self.prepare_data(data, format, **kwargs)

        # Reset buffer position to beginning
        file_buffer.seek(0)

        # Upload the buffer content
        return self.upload_file_obj(
            bucket_name=bucket_name,
            blob_name=blob_name,
            file_obj=file_buffer,
            content_type=content_type,
            metadata=metadata,
        )
