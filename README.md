# Expense Tracker MCP Server

An expense tracking application built with **FastMCP** and **SQLite**, exposed through the **Model Context Protocol (MCP)**.

The server provides tools for adding, viewing, summarizing, editing, and deleting expenses. It can be run locally for development and connected to an MCP client such as Claude Desktop, or deployed remotely as an HTTP-based MCP server.

## Features

* Add new expenses
* List expenses within a specified date range
* Summarize expenses by category
* Filter summaries by category
* Edit existing expenses
* Delete expenses
* Retrieve expense categories through an MCP resource
* SQLite-based persistent storage
* Configurable database path
* Local MCP server using `stdio`
* Remote MCP server using HTTP transport

---

## Project Structure

```text
expense-tracker-mcp-server/
│
├── main.py
├── category.json
├── expenses.db
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

### Files

| File             | Description                                                 |
| ---------------- | ----------------------------------------------------------- |
| `main.py`        | Main FastMCP server containing the MCP tools and resource   |
| `category.json`  | Contains the available expense categories and subcategories |
| `expenses.db`    | SQLite database containing stored expenses                  |
| `pyproject.toml` | Project configuration and dependencies                      |
| `uv.lock`        | Locked dependency versions for reproducible environments    |
| `.gitignore`     | Specifies files and directories excluded from Git           |
| `README.md`      | Project documentation                                       |

---

## MCP Tools

The server exposes five tools for managing expenses.

### `add_expense`

Adds a new expense to the SQLite database.

#### Parameters

| Parameter     | Type   | Description          |
| ------------- | ------ | -------------------- |
| `date`        | string | Date of the expense  |
| `amount`      | number | Amount spent         |
| `category`    | string | Expense category     |
| `subcategory` | string | Optional subcategory |
| `note`        | string | Optional note        |

#### Example

```text
Add an expense of ₹500 for food on 2026-09-05.
```

---

### `list_expenses`

Returns all expenses within a specified date range.

#### Parameters

| Parameter    | Type   | Description   |
| ------------ | ------ | ------------- |
| `start_date` | string | Starting date |
| `end_date`   | string | Ending date   |

#### Example

```text
Show my expenses from 2026-09-01 to 2026-09-05.
```

---

### `summarize_expenses`

Provides a category-wise summary of expenses for a specified date range.

#### Parameters

| Parameter    | Type   | Description              |
| ------------ | ------ | ------------------------ |
| `start_date` | string | Starting date            |
| `end_date`   | string | Ending date              |
| `category`   | string | Optional category filter |

If no category is provided, expenses are summarized across all categories.

#### Example

```text
Summarize my expenses from September 1 to September 5.
```

Example response:

```json
[
  {
    "category": "Food",
    "total": 1250.0
  },
  {
    "category": "Travel",
    "total": 800.0
  }
]
```

---

### `edit_expense`

Updates an existing expense using its ID.

#### Parameters

| Parameter     | Type    | Description          |
| ------------- | ------- | -------------------- |
| `id`          | integer | ID of the expense    |
| `amount`      | number  | Updated amount       |
| `category`    | string  | Updated category     |
| `date`        | string  | Updated date         |
| `subcategory` | string  | Optional subcategory |
| `note`        | string  | Optional note        |

#### Example

```text
Edit expense 5 and change the amount to ₹750.
```

---

### `delete_expense`

Deletes an existing expense using its ID.

#### Parameters

| Parameter | Type    | Description       |
| --------- | ------- | ----------------- |
| `id`      | integer | ID of the expense |

#### Example

```text
Delete expense 5.
```

---

## MCP Resource

The server exposes expense categories through an MCP resource:

```text
expense://category
```

The resource reads the categories from `category.json`.

This allows MCP clients to retrieve the available categories dynamically without hard-coding them into the server.

Example `category.json`:

```json
{
  "Food": [
    "Restaurant",
    "Groceries",
    "Snacks"
  ],
  "Travel": [
    "Fuel",
    "Public Transport",
    "Taxi"
  ],
  "Entertainment": [
    "Movies",
    "Games",
    "Subscriptions"
  ]
}
```

The actual categories used by the application are maintained in the project's `category.json` file.

---

## Database

The application uses **SQLite** for storing expenses.

The expense table contains:

| Column        | Type    | Description          |
| ------------- | ------- | -------------------- |
| `id`          | INTEGER | Unique expense ID    |
| `amount`      | REAL    | Expense amount       |
| `category`    | TEXT    | Expense category     |
| `date`        | TEXT    | Expense date         |
| `subcategory` | TEXT    | Optional subcategory |
| `note`        | TEXT    | Optional note        |

The default database file is:

```text
expenses.db
```

The database is initialized automatically when the server starts.

---

## Database Path Configuration

The database location can be configured using the `DB_PATH` environment variable.

The server uses the following logic:

```python
DB_Path = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "expenses.db")
)
```

If `DB_PATH` is not specified, `expenses.db` in the project directory is used.

### Windows

```powershell
$env:DB_PATH="D:\Data\expenses.db"
```

### Linux / macOS

```bash
export DB_PATH=/data/expenses.db
```

This allows the same application to use different database locations in local and remote environments without changing the source code.

---

# Local Setup

## Prerequisites

Make sure the following are installed:

* Python 3.11+
* uv
* An MCP-compatible client such as Claude Desktop

## 1. Clone the Repository

```bash
git clone <repository-url>
cd expense-tracker-mcp-server
```

## 2. Create the Environment

```bash
uv venv
```

On Windows:

```powershell
.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
uv sync
```

The `uv.lock` file ensures that the project dependencies can be installed with consistent versions.

---

## Running the Local Server

Run the server using FastMCP:

```bash
uv run fastmcp run main.py
```

The local server uses the MCP `stdio` transport and can be connected directly to compatible MCP clients.

---

# Claude Desktop

The local server can be connected to Claude Desktop through its MCP configuration.

Example configuration:

```json
{
  "mcpServers": {
    "Expense Tracker": {
      "command": "D:\\Projects\\expense-tracker-mcp-server\\.venv\\Scripts\\fastmcp.EXE",
      "args": [
        "run",
        "D:\\Projects\\expense-tracker-mcp-server\\main.py"
      ]
    }
  }
}
```

Replace the paths with the location of the project on your machine.

After updating the configuration, restart Claude Desktop.

The available tools should include:

```text
add_expense
list_expenses
summarize_expenses
edit_expense
delete_expense
```

and the resource:

```text
expense://category
```

---

# Remote Server

The same FastMCP application is also deployed as a remote MCP server.

## MCP Endpoint

```text
https://friendly-magenta-ant.fastmcp.app/mcp
```

The remote deployment runs the FastMCP server using HTTP transport.

The `/mcp` endpoint can be used by MCP clients that support remote HTTP-based MCP servers.

---

## Local vs Remote

The project supports two deployment modes using the same `main.py`.

```text
                         MCP Client
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          Local MCP Server      Remote MCP Server
              FastMCP                FastMCP
              stdio                  HTTP
                 │                     │
                 ▼                     ▼
           SQLite DB              SQLite DB
```

|                   | Local   | Remote            |
| ----------------- | ------- | ----------------- |
| FastMCP           | Yes     | Yes               |
| SQLite            | Yes     | Yes               |
| MCP Tools         | Yes     | Yes               |
| MCP Resource      | Yes     | Yes               |
| Transport         | `stdio` | HTTP              |
| Claude Desktop    | Yes     | Depends on client |
| Internet Required | No      | Yes               |

---

# Example Usage

Once the server is connected to an MCP-compatible client, expenses can be managed using natural language.

### Add an expense

```text
I spent ₹350 on food today.
```

### View expenses

```text
Show all my expenses from September 1 to September 5.
```

### Summarize expenses

```text
Give me a category-wise summary of my expenses this month.
```

### Filter by category

```text
How much did I spend on food this month?
```

### Edit an expense

```text
Change expense 12 from ₹500 to ₹650.
```

### Delete an expense

```text
Delete expense 12.
```

---

# Tech Stack

* **Python** — Application development
* **FastMCP** — MCP server implementation
* **SQLite** — Expense storage
* **aiosqlite** — Asynchronous SQLite operations
* **uv** — Python environment and dependency management
* **Model Context Protocol (MCP)** — Communication between AI clients and the server

---

# Future Improvements

Potential improvements include:

* Per-user expense isolation
* Authentication and authorization
* User profiles
* Budget tracking
* Monthly spending limits
* Recurring expenses
* Expense analytics
* CSV export
* Cloud database support
* Production-grade authentication

---

# Author

**Siddhesh**

B.Tech in Data Science and Artificial Intelligence  
IIT Bhilai
