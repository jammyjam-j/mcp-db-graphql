# mcp-db-graphql – A GraphQL API for MCP Server with Database Validation

## Overview  
`mcp-db-graphql` is a lightweight Python implementation of an Apollo Model Context Protocol (MCP) server that exposes a GraphQL API backed by a relational database. The project adds query validation middleware to enforce security rules before delegating requests to the database layer, making it suitable for AI agents and other services that require fine‑grained access control.

## Features  
- **MCP Server** – Implements the MCP protocol using Apollo’s framework.  
- **GraphQL schema** – Models users and posts with full CRUD operations.  
- **Validation middleware** – Intercepts queries, validates permissions against a JSON policy file, and logs violations.  
- **SQLAlchemy integration** – Uses SQLite for simplicity; swapable with any SQL‑Alchemy supported database.  
- **Docker support** – Ready‑to‑run container image and docker‑compose stack.  
- **Automated tests** – Unit tests for models, resolvers, and validation logic.  
- **CI pipeline** – GitHub Actions workflow that runs tests on every push.

## Tech Stack  
- Python 3.11+  
- Apollo MCP Server (`mcp-server`)  
- Graphene‑Python for GraphQL schema construction  
- SQLAlchemy ORM  
- SQLite (default)  
- Docker & docker‑compose  

## Installation  

```bash
# Clone the repository
git clone https://github.com/jammyjam-j/mcp-db-graphql

cd mcp-db-graphql

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate   # On Windows use `.venv\Scripts\activate`
pip install -r requirements.txt
```

## Usage  

### Start the server locally  
```bash
# Apply migrations (creates users and posts tables)
python scripts/seed_data.py

# Run the MCP server
python app/__init__.py
```

The server listens on `http://localhost:5000/graphql` by default.

### Example GraphQL Queries  

**Get all users**

```graphql
query {
  users {
    id
    name
    email
  }
}
```

**Create a new post**

```graphql
mutation CreatePost($title: String!, $content: String!) {
  createPost(title: $title, content: $content) {
    id
    title
    author {
      name
    }
  }
}
```

Variables:

```json
{
  "title": "Hello World",
  "content": "This is my first post."
}
```

### Using the Validation Middleware  
The middleware reads a `policy.json` file located at the project root. Add or modify rules to restrict which fields can be queried by specific roles.

Example policy snippet:

```json
{
  "roles": {
    "admin": ["*"],
    "user": ["id", "name", "email"]
  }
}
```

## API Endpoints  

The GraphQL endpoint is exposed at `/graphql`. No additional REST endpoints are provided.  
For debugging, the server also exposes a health check:

- `GET /health` – returns JSON `{ "status": "ok" }`.

## References and Resources  

1. [Apollo MCP Server - Apollo GraphQL Docs](https://www.apollographql.com/docs/apollo-mcp-server)  
2. [GitHub - gabbello/mcp-graphql: MCP server for graphQL APIs ...](https://github.com/gabbello/mcp-graphql)  
3. [Connect AI Agents to Fabric API for GraphQL with a local Model Context Protocol (MCP) server – Microsoft Learn](https://learn.microsoft.com/en-us/fabric/data-engineering/api-graphql-local-model-context-protocol)  
4. [Turn Any GraphQL API into an MCP Server | Zuplo Blog](https://zuplo.com/blog/mcp-server-graphql)  
5. [Simplifying LLM Integration with MCP and API Connect GraphQL – IBM Developer](https://developer.ibm.com/articles/awb-simplifying-llm-integration-mcp-api-connect-graphql/)  

## Contributing  

Pull requests are welcome. For major changes, open an issue first to discuss the proposed modifications.  
Please ensure tests pass (`pytest`) before submitting a PR.

GitHub repository: https://github.com/jammyjam-j/mcp-db-graphql

## License  

MIT License