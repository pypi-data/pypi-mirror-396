# CodeMie Assistants MCP Server

Python server implementing Model Context Protocol (MCP) for CodeMie Assistants operations.

## Features
- Chat with AI/Run CodeMie assistant

Note: The server requires authentication credentials via environment variables.

## API

### Tools

#### chat
Chat with a specific AI assistant
Inputs:
- `message (string)`: Message to send to assistant
- `conversation_id (string)`: Identifier of current conversation. It should be always passed if present in current communication thread.
- `history (array, optional)`: Previous conversation messages in format:
  [{"role": "user|assistant", "message": "text"}]

Returns generated assistant response as text

## Installation

Ensure you have `Python 3.12` or later installed.

**Important:** Before running the MCP server, you must configure the required environment variables (see [Environment Variables](#environment-variables) section below).

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *codemie-mcp-assistants*.

```bash
uvx codemie-mcp-assistants
```

### Using Poetry

Alternatively you can install via Poetry:

```bash
poetry install codemie-mcp-assistants
```

After installation, you can run it as a script using:

```bash
poetry run codemie-mcp-assistants
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

**Required variables:**
```json
"mcpServers": {
  "codemie": {
    "command": "uvx",
    "args": ["codemie-mcp-assistants"],
    "env": {
      "CODEMIE_ASSISTANT_ID": "your-assistant-id",
      "CODEMIE_USERNAME": "your-username",
      "CODEMIE_PASSWORD": "your-password"
    }
  }
}
```

**Optional variables (with defaults):**
```json
"env": {
  "CODEMIE_API_DOMAIN": "https://codemie.lab.epam.com/code-assistant-api",
  "CODEMIE_AUTH_CLIENT_ID": "codemie-sdk",
  "CODEMIE_AUTH_SERVER_URL": "https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth",
  "CODEMIE_AUTH_REALM_NAME": "codemie-prod"
}
```
</details>

<details>
<summary>Using poetry installation</summary>

**Required variables:**
```json
"mcpServers": {
  "codemie": {
    "command": "poetry",
    "args": ["run", "codemie-mcp-assistants"],
    "env": {
      "CODEMIE_ASSISTANT_ID": "your-assistant-id",
      "CODEMIE_USERNAME": "your-username",
      "CODEMIE_PASSWORD": "your-password"
    }
  }
}
```

**Optional variables (with defaults):**
```json
"env": {
  "CODEMIE_API_DOMAIN": "https://codemie.lab.epam.com/code-assistant-api",
  "CODEMIE_AUTH_CLIENT_ID": "codemie-sdk",
  "CODEMIE_AUTH_SERVER_URL": "https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth",
  "CODEMIE_AUTH_REALM_NAME": "codemie-prod"
}
```
</details>

### Environment Variables

#### Mandatory Variables

The following environment variables **must** be configured before running the MCP server:

**Assistant Configuration:**
- `CODEMIE_ASSISTANT_ID`: Your CodeMie assistant ID (required)

**Authentication (choose one method):**

*Option 1: Username/Password*
- `CODEMIE_USERNAME`: Your CodeMie username
- `CODEMIE_PASSWORD`: Your CodeMie password

*Option 2: Client Credentials*
- `CODEMIE_AUTH_CLIENT_SECRET`: Auth client secret

#### Optional Variables (Environment-Specific)

By default, the server connects to the **production environment** with these settings:
- `CODEMIE_API_DOMAIN`: `https://codemie.lab.epam.com/code-assistant-api`
- `CODEMIE_AUTH_CLIENT_ID`: `codemie-sdk`
- `CODEMIE_AUTH_SERVER_URL`: `https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth`
- `CODEMIE_AUTH_REALM_NAME`: `codemie-prod`

You can override these variables to point to a different environment.

**Example: Preview Environment Configuration**
```bash
CODEMIE_API_DOMAIN="https://codemie-preview.lab.epam.com/code-assistant-api"
CODEMIE_AUTH_CLIENT_ID="codemie-preview-sdk"
CODEMIE_AUTH_SERVER_URL="https://keycloak.eks-core.aws.main.edp.projects.epam.com/auth"
CODEMIE_AUTH_REALM_NAME="codemie-prod"
```

**Other Optional Variables:**
- `CODEMIE_VERIFY_SSL`: SSL verification flag (default: `true`)

## Build

### Make build:
```bash
make build
```
