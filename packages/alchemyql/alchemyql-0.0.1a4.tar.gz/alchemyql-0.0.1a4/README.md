<p>
  <img src="https://raw.githubusercontent.com/nicholasfelixwilliams/alchemyql/main/docs/logo.png" width="200" style="padding: 10px" align="left" />
  <h3 style="font-size: 3.0em; margin: 0;">Alchemy QL</h3>
  <em>Lightweight GraphQL engine powered by SQLAlchemy</em>
</p>

<p align="left">
  <img src="https://github.com/nicholasfelixwilliams/alchemyql/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI">
  <img src="https://img.shields.io/pypi/v/alchemyql?color=%2334D058&label=pypi%20package" alt="Package version">
  <img src="https://img.shields.io/pypi/pyversions/alchemyql.svg?color=%2334D058" alt="Supported Python versions">
  <img src="https://img.shields.io/static/v1?label=code%20style&message=ruff&color=black">
</p>

---

### 🚀 Key Features
Alchemy QL's key features include:

- **Read Only** - Provides read-only graphql interface into your database 
- **Data Type Support** - Currently supported data types:
    - Built in types: int, float, bool, str, bytes
    - Date types: date, datetime, time
    - Enums
    - JSON fields
    - Relationships
- **Query Options** - Currently supported query options:
    - Filtering 
    - Ordering
    - Pagination (using offset & limit)
- **Sync & Async support** 
- **Optimised SQL Queries** 
- **ORM Support** - Currently supported sqlalchemy orm:
    - Declarative base with mapping 
    - Classic declarative base 

---

### ℹ️ Installation

```sh
# Using pip
pip install alchemyql

# Using poetry
poetry add alchemyql

# Using uv
uv add alchemyql

# With FastAPI Extension
uv add alchemyql[fastapi]
```

---

### 📦 Dependencies

- <a href="https://github.com/sqlalchemy/sqlalchemy" target="_blank">Sqlalchemy</a> (v2)
- <a href="https://github.com/graphql-python/graphql-core" target="_blank">Graph QL Core</a>

---

### 📘 How to use

**Step 1** - Create your Alchemy QL engine (sync or async):

```py
from alchemyql import AlchemyQLSync, AlchemyQLAsync

sync_engine = AlchemyQLSync()
async_engine = AlchemyQLSync()
```

**Step 2** - Register your sqlalchemy tables:

```py
from your_db import Table

engine.register(
    Table, 
    include_fields=["field_one", "field_two"],
    filter_fields=["field_one"],
    order_fields=["field_one"],
    pagination=True,
    max_limit=100
    ...
)
```

**Step 3** - Build your schema:

```py
engine.build_schema()
```

**Step 4** - Run queries:

```py
query = "query { table { field } }"
db = session_factory() # SQLAlchemy DB session

# Sync Variation
res = sync_engine.execute_query(query=query, db_session=db)

# Async Variation
res = await async_engine.execute_query(query=query, db_session=db)
```

---

### 📘 Supported Options

**Engine Creation:**

| Key   | Type  | Default | Description |
| ----- | ----- | ----- | ----- |
| max_query_depth | int | None | The maximum depth allowed for nested queries | 

**Registering Table:**

| Key   | Type  | Default | Description |
| ----- | ----- | ----- | ----- |
| graphql_name | str | None | Customise the graphql type name (defaults to sql tablename) | 
| description | str | None | Customise the graphql type descripton | 
| query | bool | True | Whether to allow direct querying of table |
| include_fields | list[str] | None | Allow only specific fields to be exposed | 
| exclude_fields | list[str] | [] | Block specific fields from being exposed |
| relationships | list[str] | [] | Relationships to be exposed (target table must be registered aswell) |
| filter_fields | list[str] | [] | Allow filtering for specific fields | 
| order_fields | list[str] | [] | Allow ordering for specific fields | 
| default_order | dict[str, Order] | None | Default order to apply to queries | 
| pagination | bool | False | Whether to support pagination | 
| default_limit | int | None | Default number of records that can be returned in 1 query | 
| max_limit | int | None | Maximum number of records that can be returned in 1 query | 


**NOTE:** if you do not specify include_fields or exclude_fields it will default expose all fields.

**NOTE:** if you specify query=False, then all filtering & ordering & pagination is disabled. This is for the case where a table should only be available via a relationship

**Filtering Options:**

| Type | Supported Filters |
| ----- | ----- |
| int | eq, ne, gt, ge, lt, le, in |
| float | eq, ne, gt, ge, lt, le, in |
| bool | eq, ne |
| str | eq, ne, contains, startswith, endswith, in |
| date | eq, ne, gt, ge, lt, le, in |
| datetime | eq, ne, gt, ge, lt, le, in |
| time | eq, ne, gt, ge, lt, le, in |
| Enum | eq, ne, in |

All other types are not currently supported for filtering.

---

### 📘 Logging

AlchemyQL uses the "alchemyql" logger.

Other docs can be found in: <a href="https://github.com/nicholasfelixwilliams/alchemyql/tree/main/docs" target="_blank">docs/</a>

---

### 📘 Extensions

AlchemyQL has the following extensions:
 - FastAPI - sync and async pre-created routers available (see <a href="https://github.com/nicholasfelixwilliams/alchemyql/tree/main/docs/EXAMPLE-FASTAPI.md" target="_blank">Doc</a> )  

---

### ℹ️ License

This project is licensed under the terms of the MIT license.