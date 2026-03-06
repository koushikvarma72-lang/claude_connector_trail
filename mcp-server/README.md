# MCP Server Layout

## Structure

- `core/`: shared config, rate-limiter, metrics, and guard helpers.
- `connectors/<name>/config.py`: connector settings and env loading.
- `connectors/<name>/client.py`: API calls for the connector.
- `connectors/<name>/tools.py`: MCP tool handlers registered on `FastMCP`.

## Environment Loading

The server loads env files in this order:

1. `.env`
2. optional `.env.<connector>` files when that connector module is imported

Example connector env files:

- `.env.github`
- `.env.airtable`
- `.env.trello`
- `.env.task_manager`

Use the corresponding `*.example` files as templates.
