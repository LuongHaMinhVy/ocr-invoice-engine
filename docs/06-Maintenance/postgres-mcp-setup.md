# PostgreSQL MCP Server Configuration Guide

This guide details how to configure the PostgreSQL Model Context Protocol (MCP) server for the OCR Invoice Processing Engine. This enables MCP-compatible AI assistants (such as Cursor or Claude Desktop) to directly inspect, query, and analyze the database during development.

---

## 1. Installation

Following our workspace standards, install the PostgreSQL MCP server globally using `pnpm`:

```bash
pnpm add -g @modelcontextprotocol/server-postgres
```

Alternatively, you can run it on demand without a global installation using `pnpm dlx` in your MCP client configuration.

---

## 2. Client Configuration

### Cursor / Claude Desktop Config
To integrate the PostgreSQL MCP server, add it to your Client's MCP settings configuration file (e.g., `claude_desktop_config.json` or Cursor's MCP configuration settings).

Add the following block under the `mcpServers` object:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "pnpm",
      "args": [
        "dlx",
        "@modelcontextprotocol/server-postgres",
        "postgresql://postgres:postgres@localhost:5432/ocr_invoice"
      ]
    }
  }
}
```

> [!NOTE]
> Make sure to adjust the connection URL (`postgresql://username:password@host:port/database_name`) to match your local PostgreSQL configuration.

---

## 3. Database Health & Verification Queries

Once the MCP server is configured and connected, you can ask the assistant to run the following verification queries to inspect database health and check the table schemas.

### A. List Tables and Schemas
To verify the tables have been created successfully:
```sql
SELECT table_name, table_schema 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

### B. Inspect Invoice Table Structure
To verify the column structure of the `invoices` table:
```sql
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'invoices';
```

### C. Retrieve Latest Invoices
To verify that records are inserting and checking the most recent 10 invoices:
```sql
SELECT id, vendor_name, total_amount, status, created_at 
FROM invoices 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## 4. Troubleshooting

* **Connection Refused:** Ensure that your local PostgreSQL instance is running and accepts connections on port `5432`.
* **Authentication Failure:** Double check the username and password in the connection string.
* **pnpm command not found:** Ensure `pnpm` is globally available in your environment's PATH so the MCP client can invoke it.
