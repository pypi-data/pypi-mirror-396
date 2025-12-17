# OKO CLI

![Python](https://img.shields.io/badge/python-3.8%2B-blue)

![License](https://img.shields.io/badge/license-MIT-green)

![Status](https://img.shields.io/badge/status-beta-yellow)

![CLI](https://img.shields.io/badge/interface-CLI-lightgrey)

![Build](https://img.shields.io/badge/build-hatchling-blueviolet)

**OKO** is a minimal and elegant CLI tool for testing API endpoints directly from your terminal.

Built with care for developers who prefer working from the command line and want a lightweight alternative to tools like Postman or Insomnia — without the overhead.

---

## Features

- 📁 Collections to organize endpoints
- 🔗 Named endpoints with aliases
- 🧩 Global variables with `{{variable}}` resolution
- 🧪 Run HTTP requests from the terminal
- 🎨 Clean, readable output using Rich
- ⚙️ Simple JSON-based configuration
- 🚀 Fast workflow, zero UI distractions

---

### Installation

```bash
pip install oko-cli
```

### Getting Started

Initialize a workspace

```bash
oko init
```

This creates the local OKO workspace with configuration, collections, and variables support.

### Collections

Create a collection

```bash
oko collection create products
```

List existing collections

```bash
oko collection list
```

### Endpoints

Add an endpoint to a collection

```bash
oko endpoint add products list https://dummyjson.com/products --method GET
```

List endpoints in a collection

```bash
oko endpoint list products
```

Run an endpoint

```bash
oko endpoint run products list
```

### Variables

OKO supports global variables stored in the config file.

Add a variable

```bash
oko variable add base_url=https://dummyjson.com
```

List variables

```bash
oko variable list
```

Delete a variable

```bash
oko variable delete base_url
```

### Variable Resolution

Variables can be referenced using the {{variable}} syntax:

```bash
oko endpoint add products list {{base_url}}/products --method GET
```

Variables are automatically resolved in:

- URLs
- Query parameters
- Headers
- JSON request bodies

Nested variables are also supported:

```text
{{user.id}}
{{auth.token}}
```

### Running Requests with Options

Headers

```bash
oko endpoint run auth currentUser -H Authorization="Bearer {{token}}"
```

Query Parameters

```bash
oko endpoint run products list -p limit=3 -p page=1
```

JSON Body

```bash
oko endpoint run users create --json '{"name":"John","email":"john@example.com"}'
```

---

Output

OKO displays:

- HTTP status (color-coded)
- Method and URL
- Formatted JSON responses
- Plain text responses when applicable

Designed to be readable, focused, and terminal-friendly.

---

Philosophy

OKO is intentionally simple.

- No UI
- No accounts
- No syncing
- No cloud dependencies

Just your terminal, your endpoints, and clean output.

Built for personal use — shared in case it helps others.

---

Requirements

- Python 3.8+

---

Project Status

This project is in active development.

Current version focuses on:

- Core endpoint execution
- Collections
- Variables
- Clean CLI UX

Future versions may expand features while preserving simplicity.
