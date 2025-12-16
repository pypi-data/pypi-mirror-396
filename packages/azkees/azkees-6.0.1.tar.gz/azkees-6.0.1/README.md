# AZKees - Azure Key Vault Easy & Secure

AZKees is a Python package that provides a secure and efficient way to interact with Azure Key Vault secrets, with built-in logging support, concurrent operations, and Docker-friendly configuration.

## Features

- 🔐 Secure secret management using Azure Key Vault
- ⚡ Concurrent batch operations for better performance
- 🎯 Singleton pattern with LRU caching for optimal efficiency
- 📝 Comprehensive logging with color-coded output
- 🐳 Docker volume support for secure configuration mounting
- 🔄 Secret lifecycle management (create, update, delete, purge, recover)
- 🛡️ URL masking for sensitive data in logs
- 🌐 Platform-independent configuration (Windows/Linux)
- 📊 Support for secret metadata (tags, expiration, etc.)

## Installation

### Production Use (Recommended)

```bash
pip install azkees
```

### Using Poetry

```bash
poetry add azkees
```

### Development (Optional)

For contributing or local development only:

```bash
# Clone the repository (requires access)
git clone https://github.com/bek42/azkees.git
cd azkees

# Install in editable mode
pip install -e .

# Or using Poetry
poetry install
```

## Configuration

### Option 1: Direct Path (Recommended for Docker)

Pass the configuration path directly when initializing the client:

```python
from azkees import Az

az_client = Az(
    config_section="production",
    keys_config_path="/app/config/api_keys.ini"
)
```

### Option 2: Environment Variables

1. Create an `.env` file:

   ```env
   keys_config_linux = "/app/config/api_keys.ini"
   keys_config_windows = "C:/config/api_keys.ini"
   LOG_LEVEL = "INFO"
   ```

2. Use without explicit path:

   ```python
   from azkees import Az
   
   az_client = Az(config_section="production")
   ```

### API Keys Configuration File

Create `api_keys.ini` with your Azure credentials:

```ini
[production]
azure_tenant_id = your-tenant-id
azure_client_id = your-client-id
azure_client_secret = your-client-secret
azure_vault_url = https://your-vault.vault.azure.net/

[development]
azure_tenant_id = dev-tenant-id
azure_client_id = dev-client-id
azure_client_secret = dev-client-secret
azure_vault_url = https://dev-vault.vault.azure.net/
```

## Usage

### Basic Usage

```python
from azkees import Az

# Initialize with explicit config path (recommended for Docker)
az_client = Az(
    config_section="production",
    keys_config_path="/app/config/api_keys.ini"
)

# Retrieve a single secret
secret_dict = az_client.get_secrets(name="my-secret")
print(f"Secret value: {secret_dict['value']}")

# Retrieve multiple secrets concurrently (fast!)
secrets = az_client.get_multiple_secrets(["secret1", "secret2", "secret3"])
for name, value in secrets.items():
    print(f"{name}: {value}")

# Set a secret with metadata
az_client.set_secrets(
    name="my-secret",
    value="my-secret-value",
    tags={"environment": "production", "owner": "team-a"},
    content_type="password"
)

# Mask sensitive URLs in logs
safe_url = Az.mask_sensitive_info("postgresql://user:password@host:5432/db?token=abc123")
print(safe_url)  # postgresql://user:@host:5432/db?token=****
```

### Advanced Usage with VaultHandler

```python
from azkees import VaultHandler

# Initialize vault handler
vault = VaultHandler(
    section="production",
    keys_config_path="/app/config/api_keys.ini"
)

# Get a single secret
api_key = vault.get_secret("api-key")

# Get multiple secrets concurrently
db_secrets = vault.get_multiple_secrets([
    "db-host",
    "db-password",
    "db-username"
])

# List all secrets in vault
all_secrets = vault.list_secrets()
print(f"Found {len(all_secrets)} secrets")

# Set a new secret
vault.set_secret("new-secret", "secret-value")

# Delete a secret (soft delete)
vault.delete_secret("old-secret")

# Delete and permanently purge
vault.delete_secret("temp-secret", purge=True)

# Permanently purge a deleted secret
vault.purge_secret("deleted-secret")
```

### Singleton Pattern with Caching

```python
from azkees import AzureVaultClient

# First initialization
client1 = AzureVaultClient(
    config_section="production",
    keys_config_path="/app/config/api_keys.ini"
)

# Second call returns the same instance (singleton)
client2 = AzureVaultClient("production", "/app/config/api_keys.ini")
assert client1 is client2  # True

# Get secret with LRU caching (subsequent calls use cache)
secret = client1.get_secret("cached-secret")  # Fetches from Azure
secret = client1.get_secret("cached-secret")  # Returns from cache

# Batch operation with concurrent execution
secrets = client1.get_secrets_batch([
    "secret1", "secret2", "secret3", "secret4", "secret5"
])

# Check if vault is available
if client1.is_available:
    print("Vault connection is active")
```

## Docker Integration

### Docker Volume Mount (Recommended)

This approach keeps sensitive credentials out of your `.env` file and allows secure configuration mounting:

**docker-compose.yml:**

```yaml
services:
  app:
    image: your-app:latest
    container_name: your-app
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env  # No sensitive data here!
    volumes:
      # Mount api_keys.ini as read-only volume
      - /host/path/to/api_keys.ini:/app/config/api_keys.ini:ro
      - ./logs:/app/logs
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

**In your application:**

```python
from azkees import Az

# Use the mounted config file
az_client = Az(
    config_section="production",
    keys_config_path="/app/config/api_keys.ini"
)
```

### Full Docker Example

**Dockerfile:**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create config directory (will be mounted)
RUN mkdir -p /app/config /app/logs

# Run application
CMD ["python", "main.py"]
```

**docker-compose.yml (Complete Example):**

```yaml
services:
  backend:
    image: your-registry/your-app:production
    container_name: your-app-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - /path/to/backend-prod.env
    volumes:
      # Data persistence
      - /host/data/app:/data
      # Secure config mount (read-only)
      - /secure/location/api_keys.ini:/app/config/api_keys.ini:ro
      # Log directory
      - /host/data/app/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

### Environment Variables for Docker

Your `.env` file can now be safely committed to version control:

```env
# Application settings
APP_NAME=my-app
ENVIRONMENT=production
LOG_LEVEL=INFO

# No sensitive Azure credentials here!
# They're in the mounted api_keys.ini file
```

## API Reference

### Az Class

Main client for Azure Key Vault operations with logging.

#### Methods

- `get_secrets(name: str) -> dict`: Retrieve a secret with logging
- `get_multiple_secrets(names: List[str]) -> dict[str, str]`: Concurrent batch retrieval
- `set_secrets(name, value, *, enabled, tags, content_type, not_before, expires_on, **kwargs) -> bool`: Set secret with metadata
- `mask_sensitive_info(url: str, sensitive_keys: List[str] | None) -> str`: Static method to mask URLs

### VaultHandler Class

Centralized vault operations manager.

#### Methods

- `get_secret(key: str) -> str`: Get single secret value
- `get_multiple_secrets(keys: List[str]) -> dict[str, str]`: Concurrent batch retrieval
- `set_secret(key: str, value: str) -> bool`: Set a secret
- `list_secrets() -> List[str]`: List all vault secrets
- `delete_secret(key: str, purge: bool = False) -> bool`: Delete (and optionally purge) secret
- `purge_secret(key: str) -> bool`: Permanently delete a soft-deleted secret
- `mask_sensitive_info(url: str, sensitive_keys: Optional[List[str]]) -> str`: Static URL masking

### AzureVaultClient Class

Singleton client with LRU caching.

#### Methods

- `get_secret(secret_name: str, secret_version: Optional[str] = None) -> str`: Cached secret retrieval
- `get_secrets_batch(secret_names: List[str], max_workers: int = 5) -> Dict[str, str]`: Concurrent batch retrieval
- `is_available` (property): Check vault connection status

## Performance Features

### Concurrent Operations

Batch operations use `ThreadPoolExecutor` for parallel API calls:

```python
# Instead of 5 sequential calls (~5 seconds)
secrets = {}
for name in ["s1", "s2", "s3", "s4", "s5"]:
    secrets[name] = vault.get_secret(name)

# Use concurrent batch (~1 second)
secrets = vault.get_multiple_secrets(["s1", "s2", "s3", "s4", "s5"])
```

### LRU Caching

The `AzureVaultClient` uses `@lru_cache(maxsize=128)` for frequently accessed secrets:

```python
client = AzureVaultClient("prod", "/app/config/api_keys.ini")

# First call: fetches from Azure (~200ms)
secret = client.get_secret("api-key")

# Subsequent calls: returns from cache (~0.01ms)
secret = client.get_secret("api-key")
```

## Security Best Practices

1. **Never commit `api_keys.ini` to version control**
   - Add to `.gitignore`
   - Use Docker volume mounts for production

2. **Use read-only mounts in Docker**
   ```yaml
   volumes:
     - /secure/api_keys.ini:/app/config/api_keys.ini:ro
   ```

3. **Separate environments**
   ```ini
   [development]
   # Dev credentials
   
   [staging]
   # Staging credentials
   
   [production]
   # Production credentials
   ```

4. **Use URL masking in logs**
   ```python
   safe_url = Az.mask_sensitive_info(connection_string)
   log.info("Connecting to: %s", safe_url)
   ```

5. **Implement proper Azure RBAC**
   - Grant minimum required permissions
   - Use managed identities when possible
   - Rotate secrets regularly

## Troubleshooting

### FileNotFoundError: Configuration file not found

```python
# Make sure the path is correct
az_client = Az(
    config_section="production",
    keys_config_path="/app/config/api_keys.ini"  # Check this path
)
```

### ValueError: Configuration section not found

Check your `api_keys.ini` has the correct section:

```ini
[production]  # This must match your config_section parameter
azure_tenant_id = ...
```

### Secret not found errors

```python
try:
    secret = vault.get_secret("my-secret")
except KeyError as e:
    log.error("Secret not found: %s", e)
```

### Docker volume mount issues

```bash
# Verify the file exists on host
ls -la /host/path/to/api_keys.ini

# Check file permissions (should be readable)
chmod 644 /host/path/to/api_keys.ini

# Verify mount inside container
docker exec your-container ls -la /app/config/api_keys.ini
```

## Development

### Running Tests

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
pytest tests/

# Run with coverage
pytest --cov=azkees tests/
```

### Building for PyPI

```bash
# Build the package
poetry build

# Publish to PyPI
poetry publish
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Author

**Bharani Nitturi** - [bek42](https://github.com/bek42)

## Support

- 📧 Email: bharani.nitturi@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/bek42/azkees/issues)
- 📚 Documentation: [GitHub Wiki](https://github.com/bek42/azkees/wiki)
