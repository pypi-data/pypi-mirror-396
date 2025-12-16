# Gravi CLI

Command-line tool for Gravitate infrastructure management. Provides CLI access to mom infrastructure, allowing developers to authenticate, manage tokens, and access instance configurations and credentials.

## Features

- **OAuth-style device authorization** - Secure browser-based authentication
- **Automatic token refresh** - Tokens auto-renew when <7 days remaining
- **Token management** - List, revoke, and manage CLI tokens
- **Instance access** - Get configurations and credentials for Gravitate instances
- **Python library API** - Use programmatically in scripts and applications
- **CI/CD support** - Environment variable-based authentication

## Installation

### From Source (Development)

Using `uv` (recommended):

```bash
cd /home/jvogel/src/work/tools/mom/cli
uv pip install -e ".[test]"
```

Or with traditional pip:

```bash
cd /home/jvogel/src/work/tools/mom/cli
pip install -e ".[test]"
```

### From PyPI (Future)

```bash
pip install gravi-cli
# or
uv pip install gravi-cli
```

## Quick Start

**Note:** If you installed with `uv pip install -e .`, you can run the CLI using `uvx --from . gravi` or just `gravi` if it's in your PATH.

### 1. Login

```bash
gravi login
# or with uvx:
uvx --from . gravi login
```

This will:
1. Open your browser to mom authorization page
2. Display a user code (e.g., `ABCD-1234`)
3. Wait for you to authorize in the browser
4. Save credentials to `~/.config/gravi/config.json`

### 2. Check Status

```bash
gravi status
```

Shows:
- Current user email
- Mom URL
- Device name
- Token ID
- Token expiry

### 3. Get Instance Configuration

```bash
# Get config as JSON
gravi config dev

# Get config as environment variables
gravi config prod --format=env
```

### 4. Logout

```bash
gravi logout
```

Revokes token on server and clears local credentials.

## CLI Commands

### Authentication

```bash
gravi login                          # Authenticate via browser
gravi logout                         # Clear credentials and revoke token
gravi status                         # Show login status and token expiry
gravi whoami                         # Show current user info
```

### Token Management

```bash
gravi tokens list                    # List all CLI tokens
gravi tokens revoke <token_id>       # Revoke a specific token
gravi tokens revoke --all            # Revoke all tokens
```

### Instance Access

```bash
gravi config <instance_key>          # Get instance configuration
gravi config <instance_key> --format=env    # Get as environment variables
```

## Python Library API

Use gravi_cli programmatically in Python scripts:

```python
from gravi_cli.api import get_instance_config, get_instance_token

# Get database credentials
config = get_instance_config("prod")
db_url = config["config"]["database_url"]

# Get ServiceNow access token
token_response = get_instance_token("dev")
sn_token = token_response["access_token"]

# Get mom access token directly
from gravi_cli.api import get_mom_token
mom_token = get_mom_token()  # Auto-refreshes if needed
```

### Example: Database Connection

```python
from gravi_cli.api import get_instance_config
import psycopg2

# Get prod database credentials
config = get_instance_config("prod")
conn = psycopg2.connect(config["config"]["database_url"])

# Use database
cursor = conn.cursor()
cursor.execute("SELECT * FROM users LIMIT 10")
```

### Example: ServiceNow API

```python
from gravi_cli.api import get_instance_config, get_instance_token
import requests

# Get ServiceNow config and token
config = get_instance_config("dev")
token_response = get_instance_token("dev")

# Make ServiceNow API call
response = requests.get(
    f"{config['api_url']}/api/now/table/incident",
    headers={"Authorization": f"Bearer {token_response['access_token']}"}
)
incidents = response.json()
```

## CI/CD Usage

For automated scripts and CI/CD pipelines:

```bash
# Set refresh token as environment variable
export GRAVI_REFRESH_TOKEN="your_refresh_token_here"

# Commands will automatically use the env var
gravi config prod
```

**Getting a CI/CD token:**
1. Run `gravi login` on your local machine
2. Run `gravi tokens list` to see your token ID
3. Copy the refresh token from `~/.config/gravi/config.json`
4. Set as `GRAVI_REFRESH_TOKEN` in your CI/CD system

**Security Note:** Treat `GRAVI_REFRESH_TOKEN` like a password. Use secret management systems (GitHub Secrets, AWS Secrets Manager, etc.) to store it securely.

## Configuration

### Config File Location

`~/.config/gravi/config.json`

### Config File Format

```json
{
  "version": 1,
  "user_email": "john.doe@gravitate.com",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token_expires_at": "2025-11-09T10:30:00Z",
  "token_id": "507f1f77bcf86cd799439011",
  "device_name": "John's MacBook"
}
```

### Environment Variables

- `GRAVI_MOM_URL` - Override mom API URL (default: `https://mom.gravitate.energy`)
- `GRAVI_REFRESH_TOKEN` - CI/CD refresh token (bypasses config file)

### File Permissions

Config file is automatically set to `0600` (owner read/write only) for security.

## Token Auto-Renewal

Refresh tokens are automatically renewed when <7 days remaining:
- CLI checks expiry on each use
- If <7 days: requests new 14-day token
- Config file updated automatically
- Seamless for users - no re-login needed

## Development

### Setup

```bash
cd /home/jvogel/src/work/tools/mom/cli
pip install -e ".[test]"
```

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=gravi_cli --cov-report=term-missing

# Specific test file
pytest tests/test_config.py

# Verbose
pytest -v
```

### Project Structure

```
cli/
├── gravi_cli/
│   ├── __init__.py          # Package metadata
│   ├── api.py               # Public Python API
│   ├── auth.py              # Token refresh and auth logic
│   ├── cli.py               # CLI commands (Click)
│   ├── client.py            # Mom API client
│   ├── config.py            # Config file management
│   └── exceptions.py        # Custom exceptions
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_config.py       # Config tests
│   └── test_client.py       # API client tests
├── pyproject.toml           # Package configuration
└── README.md                # This file
```

## Troubleshooting

### "Not logged in" Error

```bash
gravi login
```

### "Token expired" Error

Tokens auto-renew, but if expired:

```bash
gravi login
```

### Rate Limiting

If you hit rate limits, wait and retry. Rate limits reset every minute.

### Mom URL Override (Development)

```bash
# Temporary override
GRAVI_MOM_URL=https://mom.dev gravi login

# Or with flag
gravi login --mom-url=https://mom.dev
```

## Security

- **Refresh tokens** stored in config file with `0600` permissions
- **Access tokens** never persisted (in-memory only)
- **No tokens in CLI arguments** (prevents shell history exposure)
- **HTTPS only** for all API calls
- **Audit logging** - All token operations logged in mom

## Support

For issues or questions:
- GitHub Issues: https://github.com/gravitate/mom/issues
- Internal Slack: #engineering

## License

MIT
