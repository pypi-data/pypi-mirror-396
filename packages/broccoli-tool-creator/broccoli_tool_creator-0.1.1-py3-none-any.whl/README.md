# Broccoli Tool Creator

A FastAPI extension that automatically creates tools in the Broccoli platform from your API endpoints with a single click in Swagger UI.

## Features

- 🚀 **One-Click Tool Creation**: Create Broccoli tools directly from Swagger UI
- 🔄 **Smart Sync**: Automatically detects existing tools and switches between Create/Update modes
- 🔐 **Automatic Authentication**: Uses AWS Cognito SRP for seamless authentication
- 🎯 **AST-Based Extraction**: Intelligently extracts endpoint metadata from your code
- 💾 **Persistent Tracking**: Tracks created tools in your database (SQLite or PostgreSQL)
- 🌐 **Proxy Support**: Access Broccoli tools through an authenticated proxy

## Installation

```bash
pip install broccoli-tool-creator
```

## Quick Start

### 1. Configure in your FastAPI app

```python
from fastapi import FastAPI
from broccoli_tool_creator import setup_tool_creator, ToolCreatorConfig

app = FastAPI(docs_url=None)  # Disable default docs

# Configure tool creator
config = ToolCreatorConfig(
    broccoli_api_url="https://your-broccoli-backend.com",
    cognito_client_id="your-client-id",
    cognito_username="your-username",
    cognito_password="your-password",
    cognito_pool_id="your-pool-id",
    owner_id="your-user-id",
    tool_tracking_db_url="postgresql://user:pass@localhost/db"  # Optional
)

# Setup tool creator (includes custom /docs)
setup_tool_creator(app, config)
```

### 2. Use in Swagger UI

1. Navigate to `/docs`
2. Find any endpoint
3. Click **"Create Tool"** or **"Update Tool"** button
4. Click **"Go to Tools"** to view in Broccoli

## Configuration

### Required Settings

```python
ToolCreatorConfig(
    broccoli_api_url="https://broccoli-backend.com",  # Broccoli API URL
    cognito_client_id="...",                          # AWS Cognito Client ID
    cognito_username="...",                           # Cognito username
    cognito_password="...",                           # Cognito password
    cognito_pool_id="...",                            # Cognito Pool ID (region_poolId)
    owner_id="...",                                   # Broccoli user ID
)
```

### Optional Settings

```python
ToolCreatorConfig(
    ...,
    tool_tracking_db_url="postgresql://...",  # External database (default: SQLite)
)
```

## Database & Persistence

By default, the tool creator uses a local SQLite database (`created_tools.db`) to track which tools have been created. This allows the UI to show "Update Tool" instead of "Create Tool" for existing tools.

### Using External Database

To use PostgreSQL or another database:

```python
from app.core.config import settings

config = ToolCreatorConfig(
    ...,
    tool_tracking_db_url=settings.DATABASE_URL
)
```

### Docker Configuration

When running in Docker, ensure your `DATABASE_URL` uses the correct hostname:

```env
# .env file
DATABASE_URL=postgresql://user:pass@postgres:5432/dbname
```

The `postgres` hostname works for inter-container communication when using docker-compose.

## Features

### Dynamic UI Buttons

The Swagger UI automatically shows context-aware buttons:

- **"Create Tool"** (Green) - For endpoints without tools
- **"Update Tool"** (Orange) - For endpoints with existing tools  
- **"Go to Tools"** (Blue) - Opens the tool in Broccoli with automatic authentication

### Smart Version Handling

The system automatically handles version conflicts:
- Detects version mismatches from the Broccoli API
- Automatically retries with the correct version
- No manual intervention required

### Authenticated Proxy

Access Broccoli tools through your backend with automatic authentication:

```
/api/v1/dev-tools/view-tool/{tool_id}
```

This endpoint:
1. Authenticates using your Cognito credentials
2. Redirects to the Broccoli tool view page
3. Proxies all requests with proper authentication headers

## API Endpoints

The package adds these endpoints to your FastAPI app:

- `POST /api/v1/dev-tools/create-from-endpoint` - Create/update a tool
- `GET /api/v1/dev-tools/check-tools` - Get list of existing tools
- `GET /api/v1/dev-tools/view-tool/{tool_id}` - View tool with authentication
- `GET /api/v1/dev-tools/broccoli-proxy/{path:path}` - Proxy to Broccoli

## Requirements

- Python 3.8+
- FastAPI 0.100.0+
- SQLAlchemy 1.4.0+
- httpx 0.24.0+
- pycognito 2024.5.1+

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
