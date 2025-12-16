import types
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from baresquare_sdk.gcp.clients import GCPClients
from baresquare_sdk.gcp.storage import Storage


class TestStorage__init__:
    def test_init_with_gcpclients_uses_injected_client(self):
        mock_storage_client = MagicMock()

        class DummyClients(GCPClients):
            pass

        mock_clients = object.__new__(DummyClients)
        mock_clients.storage = MagicMock(return_value=mock_storage_client)

        storage = Storage(source=mock_clients)

        assert storage._client is mock_storage_client
        mock_clients.storage.assert_called_once_with()

    @patch("baresquare_sdk.gcp.storage.GoogleAuth")
    @patch("baresquare_sdk.gcp.storage.storage.Client")
    def test_init_with_credentialprovider_and_no_quota_uses_project_id(self, mock_client_cls, mock_google_auth):
        mock_credentials = MagicMock()
        mock_credentials.project_id = "test-project"

        # Pass an object that implements get_credentials directly
        class DummyCreds:
            def get_credentials(self, scopes=None):
                return mock_credentials

        storage = Storage(source=DummyCreds())

        mock_client_cls.assert_called_once_with(credentials=mock_credentials, project="test-project")
        assert isinstance(storage, Storage)

    @patch("baresquare_sdk.gcp.storage.storage.Client")
    def test_init_with_quota_project_overrides_credentials_project(self, mock_client_cls):
        mock_credentials = types.SimpleNamespace(project_id="creds-project")

        class DummyCreds:
            def get_credentials(self, scopes=None):
                return mock_credentials

        _ = Storage(source=DummyCreds(), quota_project="explicit-project")

        mock_client_cls.assert_called_once_with(credentials=mock_credentials, project="explicit-project")

    @patch("baresquare_sdk.gcp.storage.storage.Client")
    def test_init_without_provider_defaults_to_googleauth(self, mock_client_cls):
        # Passing a non-credential, non-GCPClients object triggers default GoogleAuth()
        with patch("baresquare_sdk.gcp.storage.GoogleAuth") as mock_google_auth:
            mock_credentials = MagicMock(project_id=None)
            mock_google_auth.return_value.get_credentials.return_value = mock_credentials

            _ = Storage(source=object())

            mock_google_auth.assert_called_once_with()
            mock_client_cls.assert_called_once_with(credentials=mock_credentials, project=None)


class TestStorage_get_bucket:
    def test_get_bucket_calls_client_bucket(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket

        storage = object.__new__(Storage)
        storage._client = mock_client

        result = Storage.get_bucket(storage, "test-bucket")

        mock_client.bucket.assert_called_once_with("test-bucket")
        assert result == mock_bucket


class TestStorage_get_blob:
    def test_get_blob_calls_bucket_blob(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        result = Storage.get_blob(storage, "test-bucket", "test-blob")

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        assert result == mock_blob


class TestStorage_upload_file:
    def test_upload_file_calls_blob_upload_from_filename(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        result = Storage.upload_file(
            storage,
            bucket_name="test-bucket",
            blob_name="test-blob",
            file_path="test-file.txt",
            content_type="text/plain",
            metadata={"key": "value"},
        )

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        assert mock_blob.content_type == "text/plain"
        assert mock_blob.metadata == {"key": "value"}
        mock_blob.upload_from_filename.assert_called_once_with("test-file.txt")
        assert result == mock_blob

    def test_upload_file_with_pathlib_path(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        file_path = Path("test-file.txt")
        Storage.upload_file(storage, "test-bucket", "test-blob", file_path)

        mock_blob.upload_from_filename.assert_called_once_with("test-file.txt")


class TestStorage_upload_bytes:
    def test_upload_bytes_calls_blob_upload_from_string(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        data = b"test data"
        result = Storage.upload_bytes(
            storage,
            bucket_name="test-bucket",
            blob_name="test-blob",
            data=data,
            content_type="application/octet-stream",
            metadata={"key": "value"},
        )

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        assert mock_blob.content_type == "application/octet-stream"
        assert mock_blob.metadata == {"key": "value"}
        mock_blob.upload_from_string.assert_called_once_with(data)
        assert result == mock_blob


class TestStorage_upload_file_obj:
    def test_upload_file_obj_calls_blob_upload_from_file(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        file_obj = BytesIO(b"test data")
        result = Storage.upload_file_obj(
            storage, bucket_name="test-bucket", blob_name="test-blob", file_obj=file_obj, content_type="text/plain"
        )

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        assert mock_blob.content_type == "text/plain"
        mock_blob.upload_from_file.assert_called_once_with(file_obj)
        assert result == mock_blob


class TestStorage_download_file:
    def test_download_file_calls_blob_download_to_filename(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        Storage.download_file(storage, "test-bucket", "test-blob", "output.txt")

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        mock_blob.download_to_filename.assert_called_once_with("output.txt")

    def test_download_file_with_pathlib_path(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        destination_path = Path("output.txt")
        Storage.download_file(storage, "test-bucket", "test-blob", destination_path)

        mock_blob.download_to_filename.assert_called_once_with("output.txt")


class TestStorage_download_bytes:
    def test_download_bytes_calls_blob_download_as_bytes(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        result = Storage.download_bytes(storage, "test-bucket", "test-blob")

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        mock_blob.download_as_bytes.assert_called_once_with()
        assert result == mock_blob.download_as_bytes.return_value


class TestStorage_download_to_file_obj:
    def test_download_to_file_obj_calls_blob_download_to_file(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        file_obj = BytesIO()
        Storage.download_to_file_obj(storage, "test-bucket", "test-blob", file_obj)

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        mock_blob.download_to_file.assert_called_once_with(file_obj)


class TestStorage_exists:
    def test_exists_calls_blob_exists(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_blob.exists.return_value = True
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        result = Storage.exists(storage, "test-bucket", "test-blob")

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        mock_blob.exists.assert_called_once_with()
        assert result is True


class TestStorage_delete_blob:
    def test_delete_blob_calls_blob_delete(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        storage = object.__new__(Storage)
        storage._client = mock_client

        Storage.delete_blob(storage, "test-bucket", "test-blob")

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        mock_blob.delete.assert_called_once_with()


class TestStorage_list_blobs:
    def test_list_blobs_calls_bucket_list_blobs(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blobs = [MagicMock(), MagicMock()]
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = mock_blobs

        storage = object.__new__(Storage)
        storage._client = mock_client

        result = Storage.list_blobs(storage, "test-bucket")

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.list_blobs.assert_called_once_with(prefix=None, delimiter=None, max_results=None)
        assert result == mock_blobs

    def test_list_blobs_with_parameters(self):
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blobs = [MagicMock()]
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = mock_blobs

        storage = object.__new__(Storage)
        storage._client = mock_client

        result = Storage.list_blobs(storage, "test-bucket", prefix="data/", delimiter="/", max_results=10)

        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.list_blobs.assert_called_once_with(prefix="data/", delimiter="/", max_results=10)
        assert result == mock_blobs
