# GCP Secret Manager with Baresquare SDK

This guide shows how to use the Baresquare SDK to interact with Google Cloud Secret Manager.

## Initialize

### Without GCPClients

```python
from dotenv import load_dotenv
from baresquare_sdk.gcp.authentication import GoogleAuth
from baresquare_sdk.gcp.secret_manager import SecretManager

# Setup
auth = GoogleAuth()  # Uses Application Default Credentials
secret_manager = SecretManager(auth, project_id="your-project-id")

# Get a secret
api_key = secret_manager.get_secret("my-api-key")
```

### Using with GCPClients

```python
from baresquare_sdk.gcp.authentication import GoogleAuth
from baresquare_sdk.gcp.secret_manager import SecretManager
from baresquare_sdk.gcp.clients import GCPClients

# Create clients for multiple services
auth = GoogleAuth()
clients = GCPClients(auth, quota_project="your-project-id")

# Use SecretManager with GCPClients
secret_manager = SecretManager(clients, project_id="your-project-id")

# You can also use other services
# bq_client = clients.bigquery()
# drive_client = clients.drive()
```

## Examples

```python
# Get string value
api_key = secret_manager.get_secret("my-api-key")

# Get JSON value
config = secret_manager.get_secret("my-config", return_json=True)

# Get specific version
old_key = secret_manager.get_secret("my-api-key", version="1")
```

```python
certificate = secret_manager.get_secret_bytes("ssl-certificate")
```

```python
secrets = secret_manager.list_secrets()
print(f"Available secrets: {secrets}")
```

```python
if secret_manager.secret_exists("important-secret"):
    value = secret_manager.get_secret("important-secret")
```

## Required Permissions

Your service account needs the following IAM role:

- **Secret Manager Secret Accessor** (recommended)

Or create a custom role with these permissions:

- `secretmanager.versions.access`
- `secretmanager.secrets.list`
