import json
from unittest.mock import MagicMock

import pytest
from google.api_core import exceptions

from baresquare_sdk.gcp.clients import GCPClients
from baresquare_sdk.gcp.secret_manager import SecretManager


class TestSecretManager__init__:
    def test_init_with_gcpclients_uses_injected_client(self):
        """Test that SecretManager uses the client from GCPClients when provided."""
        mock_client = MagicMock()
        mock_clients = MagicMock(spec=GCPClients)
        mock_clients.secret_manager.return_value = mock_client
        mock_clients._quota_project = "test-project"

        secret_manager = SecretManager(source=mock_clients, project_id="test-project")

        assert secret_manager._client is mock_client
        assert secret_manager._project_id == "test-project"
        mock_clients.secret_manager.assert_called_once_with()


class TestSecretManagerGetSecret:
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.secret_manager = SecretManager.__new__(SecretManager)
        self.secret_manager._client = self.mock_client
        self.secret_manager._project_id = "test-project"

    def test_get_secret_returns_string_value(self):
        """Test that get_secret returns the secret value as a string."""
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"
        self.mock_client.access_secret_version.return_value = mock_response

        result = self.secret_manager.get_secret("my-secret")

        assert result == "secret-value"
        self.mock_client.access_secret_version.assert_called_once_with(
            name="projects/test-project/secrets/my-secret/versions/latest"
        )

    def test_get_secret_with_custom_version(self):
        """Test that get_secret uses the specified version."""
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"
        self.mock_client.access_secret_version.return_value = mock_response

        result = self.secret_manager.get_secret("my-secret", version="1")

        assert result == "secret-value"
        self.mock_client.access_secret_version.assert_called_once_with(
            name="projects/test-project/secrets/my-secret/versions/1"
        )

    def test_get_secret_returns_json_when_requested(self):
        """Test that get_secret returns parsed JSON when return_json=True."""
        secret_data = {"api_key": "test-key", "url": "https://api.example.com"}
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = json.dumps(secret_data)
        self.mock_client.access_secret_version.return_value = mock_response

        result = self.secret_manager.get_secret("my-secret", return_json=True)

        assert result == secret_data

    def test_get_secret_raises_runtime_error_on_not_found(self):
        """Test that get_secret raises RuntimeError when secret is not found."""
        self.mock_client.access_secret_version.side_effect = exceptions.NotFound("Secret not found")

        with pytest.raises(RuntimeError, match="Secret my-secret not found"):
            self.secret_manager.get_secret("my-secret")

    def test_get_secret_raises_runtime_error_on_general_exception(self):
        """Test that get_secret raises RuntimeError on general exceptions."""
        self.mock_client.access_secret_version.side_effect = Exception("Network error")

        with pytest.raises(RuntimeError, match="Error retrieving secret my-secret: Network error"):
            self.secret_manager.get_secret("my-secret")

    def test_get_secret_raises_value_error_when_no_project_id(self):
        """Test that get_secret raises ValueError when project_id is not set."""
        self.secret_manager._project_id = None

        with pytest.raises(ValueError, match="project_id must be set"):
            self.secret_manager.get_secret("my-secret")


class TestSecretManagerGetSecretBytes:
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.secret_manager = SecretManager.__new__(SecretManager)
        self.secret_manager._client = self.mock_client
        self.secret_manager._project_id = "test-project"

    def test_get_secret_bytes_returns_bytes(self):
        """Test that get_secret_bytes returns the secret value as bytes."""
        mock_response = MagicMock()
        mock_response.payload.data = b"secret-bytes-data"
        self.mock_client.access_secret_version.return_value = mock_response

        result = self.secret_manager.get_secret_bytes("my-secret")

        assert result == b"secret-bytes-data"
        self.mock_client.access_secret_version.assert_called_once_with(
            name="projects/test-project/secrets/my-secret/versions/latest"
        )

    def test_get_secret_bytes_with_custom_version(self):
        """Test that get_secret_bytes uses the specified version."""
        mock_response = MagicMock()
        mock_response.payload.data = b"secret-bytes-data"
        self.mock_client.access_secret_version.return_value = mock_response

        result = self.secret_manager.get_secret_bytes("my-secret", version="2")

        assert result == b"secret-bytes-data"
        self.mock_client.access_secret_version.assert_called_once_with(
            name="projects/test-project/secrets/my-secret/versions/2"
        )

    def test_get_secret_bytes_raises_runtime_error_on_not_found(self):
        """Test that get_secret_bytes raises RuntimeError when secret is not found."""
        self.mock_client.access_secret_version.side_effect = exceptions.NotFound("Secret not found")

        with pytest.raises(RuntimeError, match="Secret my-secret not found"):
            self.secret_manager.get_secret_bytes("my-secret")

    def test_get_secret_bytes_raises_value_error_when_no_project_id(self):
        """Test that get_secret_bytes raises ValueError when project_id is not set."""
        self.secret_manager._project_id = None

        with pytest.raises(ValueError, match="project_id must be set"):
            self.secret_manager.get_secret_bytes("my-secret")


class TestSecretManagerListSecrets:
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.secret_manager = SecretManager.__new__(SecretManager)
        self.secret_manager._client = self.mock_client
        self.secret_manager._project_id = "test-project"

    def test_list_secrets_returns_secret_names(self):
        """Test that list_secrets returns a list of secret names."""
        mock_secret1 = MagicMock()
        mock_secret1.name = "projects/test-project/secrets/secret1"
        mock_secret2 = MagicMock()
        mock_secret2.name = "projects/test-project/secrets/secret2"

        mock_secrets = [mock_secret1, mock_secret2]
        self.mock_client.list_secrets.return_value = mock_secrets

        result = self.secret_manager.list_secrets()

        assert result == ["secret1", "secret2"]
        self.mock_client.list_secrets.assert_called_once_with(request={"parent": "projects/test-project"})

    def test_list_secrets_raises_value_error_when_no_project_id(self):
        """Test that list_secrets raises ValueError when project_id is not set."""
        self.secret_manager._project_id = None

        with pytest.raises(ValueError, match="project_id must be set"):
            self.secret_manager.list_secrets()

    def test_list_secrets_raises_runtime_error_on_exception(self):
        """Test that list_secrets raises RuntimeError on general exceptions."""
        self.mock_client.list_secrets.side_effect = Exception("API error")

        with pytest.raises(RuntimeError, match="Error listing secrets: API error"):
            self.secret_manager.list_secrets()


class TestSecretManagerSecretExists:
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = MagicMock()
        self.secret_manager = SecretManager.__new__(SecretManager)
        self.secret_manager._client = self.mock_client
        self.secret_manager._project_id = "test-project"

    def test_secret_exists_returns_true_when_secret_exists(self):
        """Test that secret_exists returns True when secret is found."""
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "secret-value"
        self.mock_client.access_secret_version.return_value = mock_response

        result = self.secret_manager.secret_exists("my-secret")

        assert result is True

    def test_secret_exists_returns_false_when_secret_not_found(self):
        """Test that secret_exists returns False when secret is not found."""
        self.mock_client.access_secret_version.side_effect = exceptions.NotFound("Secret not found")

        result = self.secret_manager.secret_exists("my-secret")

        assert result is False

    def test_secret_exists_returns_false_on_any_exception(self):
        """Test that secret_exists returns False on any exception."""
        self.mock_client.access_secret_version.side_effect = Exception("Any error")

        result = self.secret_manager.secret_exists("my-secret")

        assert result is False


class TestSecretManagerIntegration:
    """Integration tests that test the full flow with mocked dependencies."""

    def test_full_workflow_with_gcpclients(self):
        """Test the full workflow using GCPClients directly."""
        # Setup mocks
        mock_client = MagicMock()
        mock_clients = MagicMock(spec=GCPClients)
        mock_clients.secret_manager.return_value = mock_client
        mock_clients._quota_project = "test-project"

        # Mock secret response
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "my-secret-value"
        mock_client.access_secret_version.return_value = mock_response

        # Test
        secret_manager = SecretManager(mock_clients, project_id="test-project")

        result = secret_manager.get_secret("my-secret")

        assert result == "my-secret-value"
        mock_clients.secret_manager.assert_called_once_with()
