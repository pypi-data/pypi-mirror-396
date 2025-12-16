"""GCP Secret Manager utilities for interacting with Google Cloud Secret Manager.

This module provides functions for retrieving secrets from Google Cloud Secret Manager.
"""

import json
from typing import Any

from google.api_core import exceptions

from baresquare_sdk.core.logger import logger
from baresquare_sdk.gcp.authentication import CredentialProvider, GoogleAuth
from baresquare_sdk.gcp.clients import GCPClients


class SecretManager:
    """Google Cloud Secret Manager client for reading secrets."""

    _SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

    def __init__(self, source: CredentialProvider | GCPClients, project_id: str | None = None):
        """Initialize the Secret Manager client.

        Args:
            source: Either a CredentialProvider or GCPClients instance.
            project_id: The GCP project ID. If not provided, will be inferred from credentials.
        """
        if isinstance(source, GCPClients):
            self._client = source.secret_manager()
            self._project_id = project_id or source._quota_project
            return

        # If source is a CredentialProvider, create GCPClients to get the client
        creds = source if isinstance(source, CredentialProvider) else GoogleAuth()
        clients = GCPClients(creds, quota_project=project_id)
        self._client = clients.secret_manager()
        self._project_id = project_id or clients._quota_project

    def get_secret(self, secret_name: str, return_json: bool = False, version: str = "latest") -> str | dict[str, Any]:
        """Retrieve a secret from GCP Secret Manager.

        Args:
            secret_name: The name of the secret to retrieve (e.g. 'prod-ai_agents-openai-api_key').
            return_json: Whether to parse the secret value as JSON. Defaults to False.
            version: The version of the secret to retrieve. Defaults to "latest".

        Returns:
            The secret value as either a string or JSON object.

        Raises:
            RuntimeError: If the secret cannot be retrieved or parsed.
        """
        if not self._project_id:
            raise ValueError("project_id must be set")

        try:
            # Build the resource name of the secret version
            name = f"projects/{self._project_id}/secrets/{secret_name}/versions/{version}"

            # Access the secret version
            response = self._client.access_secret_version(name=name)
            secret_value = response.payload.data.decode("UTF-8")

            # Try to parse as JSON, if it fails return as string
            if return_json:
                return json.loads(secret_value)
            return secret_value

        except exceptions.NotFound:
            logger.error(f"Secret {secret_name} not found")
            raise RuntimeError(f"Secret {secret_name} not found")
        except Exception as e:
            logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
            raise RuntimeError(f"Error retrieving secret {secret_name}: {str(e)}")

    def get_secret_bytes(self, secret_name: str, version: str = "latest") -> bytes:
        """Retrieve a secret value from Google Cloud Secret Manager as bytes.

        Args:
            secret_name: The name of the secret to retrieve.
            version: The version of the secret to retrieve. Defaults to "latest".

        Returns:
            The secret value as bytes.

        Raises:
            RuntimeError: If the secret cannot be retrieved.
        """
        if not self._project_id:
            raise ValueError("project_id must be set")

        try:
            # Build the resource name of the secret version
            name = f"projects/{self._project_id}/secrets/{secret_name}/versions/{version}"

            # Access the secret version
            response = self._client.access_secret_version(name=name)
            return response.payload.data

        except exceptions.NotFound:
            logger.error(f"Secret {secret_name} not found")
            raise RuntimeError(f"Secret {secret_name} not found")
        except Exception as e:
            logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
            raise RuntimeError(f"Error retrieving secret {secret_name}: {str(e)}")

    def list_secrets(self) -> list[str]:
        """List all secrets in the project.

        Returns:
            A list of secret names in the project.

        Raises:
            ValueError: If project_id is not set.
        """
        if not self._project_id:
            raise ValueError("project_id must be set")

        try:
            parent = f"projects/{self._project_id}"
            secrets = self._client.list_secrets(request={"parent": parent})

            secret_names = []
            for secret in secrets:
                # Extract secret name from the full resource name
                secret_name = secret.name.split("/")[-1]
                secret_names.append(secret_name)

            return secret_names

        except Exception as e:
            logger.error(f"Error listing secrets: {str(e)}")
            raise RuntimeError(f"Error listing secrets: {str(e)}")

    def secret_exists(self, secret_name: str) -> bool:
        """Check if a secret exists in the project.

        Args:
            secret_name: The name of the secret to check.

        Returns:
            True if the secret exists, False otherwise.
        """
        try:
            self.get_secret(secret_name)
            return True
        except Exception:
            return False
