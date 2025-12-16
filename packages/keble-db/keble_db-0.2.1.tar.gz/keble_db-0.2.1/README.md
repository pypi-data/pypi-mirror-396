# Keble-DB

A comprehensive database toolkit providing CRUD operations for MongoDB, SQL, and Qdrant databases with both synchronous and asynchronous support.

## Installation

```bash
pip install keble-db
```

## Key Features

- **CRUD Operations**: Complete Create, Read, Update, Delete operations for different databases
- **Dual API Support**: Both synchronous and asynchronous interfaces
- **Multiple Database Support**: MongoDB, SQL (SQLAlchemy/SQLModel), Qdrant vector database, and Neo4j graph database
- **FastAPI Integration**: Specialized dependency injection utilities for FastAPI
- **Extended Redis Support**: Enhanced Redis functionality with namespace management and batch operations
- **Pydantic Integration**: Fully compatible with Pydantic v2 for data validation

## Schemas

The package provides essential schemas for database operations:

- **QueryBase**: Used throughout the package for creating consistent queries
- **ObjectId**: Custom ObjectId implementation for use with Pydantic (you cannot use bson.ObjectId directly in Pydantic)

```python
from keble_db.schemas import QueryBase, ObjectId

# Create a query with filters
# Note: filters and order_by vary by database type
query = QueryBase(
    filters={"name": "test"},  # MongoDB: dict with query operators, SQL: list of expressions, Qdrant: dict
    limit=10,
    offset=0,
    # Order by fields vary by database type:
    # MongoDB: list of tuples [(field_name, ASCENDING/DESCENDING)]
    # SQL: list of SQLAlchemy expressions
    # Qdrant: not applicable for vector similarity search
    order_by=[("created_at", -1)]  # MongoDB example
)

# Using ObjectId with Pydantic
from pydantic import BaseModel

class MyModel(BaseModel):
    id: ObjectId
    name: str
```

## QueryBase Implementation Details

The `QueryBase` class is used to build queries across different database types, but its fields have different expectations depending on the database type:

### MongoDB QueryBase

```python
from keble_db.schemas import QueryBase
from pymongo import ASCENDING, DESCENDING

# MongoDB uses dict for filters with MongoDB query operators
query = QueryBase(
    filters={"name": "John", "age": {"$gt": 18}},  # MongoDB query dict
    limit=10,
    offset=0,  # MongoDB requires int offset
    order_by=[("created_at", DESCENDING), ("name", ASCENDING)]  # List of (field, direction) tuples
)
```

### SQL QueryBase

```python
from keble_db.schemas import QueryBase
from sqlmodel import select
from mymodels import User  # Your SQLModel

# SQL uses list of SQLAlchemy expressions for filters
query = QueryBase(
    filters=[User.age > 18, User.name == "John"],  # List of SQLAlchemy expressions
    limit=10,
    offset=0,  # SQL requires int offset
    order_by=[User.created_at.desc(), User.name.asc()]  # List of SQLAlchemy expression objects
)
```

### Qdrant QueryBase

```python
from keble_db.schemas import QueryBase

# For Qdrant search operations (with int offset)
search_query = QueryBase(
    filters={"name": {"$eq": "Test Item"}},  # Qdrant filter dict
    limit=10,
    offset=0,  # For search: integer offset
    # order_by is not applicable for vector similarity search
)

# For Qdrant scroll operations (with string point_id as offset)
scroll_query = QueryBase(
    filters={"name": {"$eq": "Test Item"}},  # Qdrant filter dict
    limit=10,
    offset="some_point_id",  # For scroll: string point_id as offset
    # order_by is not applicable for vector similarity search
)
```

## Creating CRUD Classes

You can define custom CRUD classes by extending the base classes for each database type:

### MongoDB CRUD Class

```python
from pydantic import BaseModel
from keble_db.crud.mongo import MongoCRUDBase

# Define your model
class UserModel(BaseModel):
    name: str
    email: str
    age: int

# Define your CRUD class
class CRUDUser(MongoCRUDBase[UserModel]):
    # You can add custom methods here
    pass

# Initialize the CRUD instance
user_crud = CRUDUser(
    model=UserModel,
    collection="users",
    database="my_database"
)
```

### SQL CRUD Class

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from keble_db.crud.sql import SqlCRUDBase

# Define your model
class UserModel(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str
    age: int

# Define your CRUD class
class CRUDUser(SqlCRUDBase[UserModel]):
    # You can add custom methods here
    pass

# Initialize the CRUD instance
user_crud = CRUDUser(
    model=UserModel,
    table_name="users"
)
```

### Qdrant CRUD Class

```python
from pydantic import BaseModel
from typing import List
from keble_db.crud.qdrant import QdrantCRUDBase

# Define your models
class VectorModel(BaseModel):
    vector: List[float]

class ItemModel(BaseModel):
    id: int
    name: str
    description: str

# Define your CRUD class
class CRUDItem(QdrantCRUDBase[ItemModel, VectorModel]):
    # You can add custom methods here
    pass

# Initialize the CRUD instance
item_crud = CRUDItem(
    model=ItemModel,
    vector_model=VectorModel,
    collection="items"
)
```

### Neo4j CRUD Class

```python
from pydantic import BaseModel
from keble_db.crud import Neo4jCRUDBase
from keble_db.schemas import QueryBase


class Person(BaseModel):
    id: int  # stored as a property, not the internal Neo4j id
    name: str
    age: int


class CRUDPerson(Neo4jCRUDBase[Person]):
    def __init__(self):
        super().__init__(model=Person, label="Person", id_field="id")


crud_person = CRUDPerson()

# Create
crud_person.create(neo4j_session, obj_in=Person(id=1, name="Alice", age=30))

# Query with filters/order/limit/offset
people = crud_person.get_multi(
    neo4j_session,
    query=QueryBase(filters={"age": {"$gt": 20}}, order_by=[("age", "asc")]),
)

# Relationships
crud_person.create_relationship(neo4j_session, from_id=1, to_id=2, rel_type="KNOWS")
friends = crud_person.get_related(neo4j_session, _id=1, rel_type="KNOWS")
```

Neo4j `QueryBase` expectations:
- `filters`: dict of property predicates. Supported operators: `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$contains`, `$startswith`, `$endswith`.
- `order_by`: list of `(field, "asc"|"desc")` tuples.
- `offset`/`limit`: integers mapped to `SKIP`/`LIMIT`.
- `id`/`ids`: matched against the configured `id_field` (or internal id if `use_internal_id=True`).
```

#### Neo4j internal ids (elementId)

To work with Neo4j’s internal ids without using the deprecated `id()` function, enable `use_internal_id=True` and pick a property name to store the `elementId`:

```python
# Internal-id mode uses elementId(n) and stores it on the node under node_id
crud_internal = Neo4jCRUDBase(
    model=Person,
    label="Person",
    id_field="node_id",
    use_internal_id=True,
)

created = crud_internal.create(neo4j_session, obj_in=Person(id=1, name="Internal", age=30))
print(created.node_id)  # e.g. "4:baa58b47-2a59-4aeb-b473-6953e3d50609:1"

# Query by internal id
found = crud_internal.first(
    neo4j_session,
    query=QueryBase(id=created.node_id, filters={"tag": "__keble_db_test__"}),
)

# Relationships also accept the stored elementId strings
crud_internal.create_relationship(
    neo4j_session, from_id=created.node_id, to_id=another.node_id, rel_type="KNOWS"
)
```

Notes:
- `elementId` values are strings; they differ from legacy integer `id(n)` values.
- When `use_internal_id=True`, the provided `id_field` is omitted from the write payload and rehydrated from `elementId(n)` after creation.

## Database Operations by Type

### MongoDB CRUD Operations

The MongoDB CRUD interface provides methods for working with MongoDB collections.

```python
from keble_db.crud.mongo import MongoCRUDBase
from pymongo import MongoClient, ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from keble_db.schemas import QueryBase

# Define your model
class User(BaseModel):
    name: str
    email: str
    age: int

# Create a CRUD instance
user_crud = MongoCRUDBase(
    model=User,
    collection="users",
    database="my_database"
)

# Synchronous operations
mongo_client = MongoClient("mongodb://localhost:27017")

# Create a document
user = User(name="John", email="john@example.com", age=30)
# Returns pymongo.results.InsertOneResult
result = user_crud.create(mongo_client, obj_in=user)

# Read documents
# MongoDB QueryBase usage
query = QueryBase(
    filters={"name": "John"},  # MongoDB uses dict for filters with query operators
    limit=10,
    offset=0,
    order_by=[("created_at", DESCENDING)]  # List of (field, direction) tuples
)

# First returns a User model instance or None
user = user_crud.first(mongo_client, query=query)
# get_multi returns a list of User model instances
users = user_crud.get_multi(mongo_client, query=QueryBase(limit=10, offset=0))

# MongoDB _id is typically a bson.ObjectId
user_by_id = user_crud.first_by_id(mongo_client, _id="6463a8880f23dfd71c67c487")  # ObjectId as string
# Integers are not valid ObjectIds; pass a string or bson.ObjectId (lists are also supported and will be converted).

# Update a document
# Returns pymongo.results.UpdateResult
update_result = user_crud.update(mongo_client, _id="6463a8880f23dfd71c67c487", obj_in={"age": 31})

# Delete documents
# Returns pymongo.results.DeleteResult
delete_result = user_crud.delete(mongo_client, _id="6463a8880f23dfd71c67c487")
delete_multi_result = user_crud.delete_multi(mongo_client, query=QueryBase(filters={"age": {"$lt": 18}}))

# Asynchronous operations with motor client
async_mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")

# Create a document asynchronously
user = User(name="Jane", email="jane@example.com", age=28)
result = await user_crud.acreate(async_mongo_client, obj_in=user)

# Read documents asynchronously
user = await user_crud.afirst(async_mongo_client, query=QueryBase(filters={"name": "Jane"}))
users = await user_crud.aget_multi(async_mongo_client, query=QueryBase(limit=10, offset=0))
user_by_id = await user_crud.afirst_by_id(async_mongo_client, _id="6463a8880f23dfd71c67c487")

# Update a document asynchronously
update_result = await user_crud.aupdate(async_mongo_client, _id="6463a8880f23dfd71c67c487", obj_in={"age": 29})

# Delete documents asynchronously
delete_result = await user_crud.adelete(async_mongo_client, _id="6463a8880f23dfd71c67c487")
delete_multi_result = await user_crud.adelete_multi(async_mongo_client, query=QueryBase(filters={"age": {"$lt": 18}}))

# Aggregate operations (MongoDB specific)
from typing import List
class AggregationResult(BaseModel):
    _id: int
    count: int

aggregated_data = user_crud.aggregate(
    mongo_client,
    pipelines=[{"$group": {"_id": "$age", "count": {"$sum": 1}}}],
    model=AggregationResult
)

# Async aggregate operations (MongoDB specific)
aggregated_data = await user_crud.aaggregate(
    async_mongo_client,
    pipelines=[{"$group": {"_id": "$age", "count": {"$sum": 1}}}],
    model=AggregationResult
)
```

### SQL CRUD Operations

The SQL CRUD interface provides methods for working with SQL databases via SQLModel/SQLAlchemy.

```python
from keble_db.crud.sql import SqlCRUDBase
```

#### Synchronous SQL Operations

```python
from keble_db.crud.sql import SqlCRUDBase
from sqlmodel import Session, SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4

# Define your model
class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str
    active: bool = True

# Initialize CRUD instance
user_crud = SqlCRUDBase[User](
    model=User,
    table_name="users"
)

# Create a DB session
from sqlmodel import create_engine, Session

engine = create_engine("sqlite:///database.db")
session = Session(engine)

# Create a new user
new_user = User(name="John Doe", email="john@example.com")
# Returns User instance with ID populated
user = user_crud.create(session, obj=new_user)

# QueryBase usage for SQL
from keble_db.schemas import QueryBase

query = QueryBase(
    filters=[User.active == True, User.name.contains("John")],  # List of SQLAlchemy expressions
    limit=10,
    offset=0,
    order_by=[User.name.asc(), User.email.desc()]  # List of SQLAlchemy order expressions
)

# Get a single user
# Returns User instance or None
user = user_crud.first(session, query=query)

# Get multiple users
# Returns list of User instances
users = user_crud.get_multi(session, query=query)

# Update a user
# Returns updated User instance or None if not found
user.name = "Jane Doe"
updated_user = user_crud.update(session, _id=user.id, obj=user)

# Delete a user
# Returns boolean (True if user was deleted)
result = user_crud.delete(session, _id=user.id)

# Count users
# Returns integer count
count = user_crud.count(session, query=query)

# Create multiple users
from typing import List
users: List[User] = [
    User(name="User 1", email="user1@example.com"),
    User(name="User 2", email="user2@example.com"),
    User(name="User 3", email="user3@example.com"),
]
# Returns list of created User instances
created_users = user_crud.create_multi(session, objs_in=users)

# Delete multiple users
# Returns number of deleted records
deleted_count = user_crud.delete_multi(session, query=query)
```

#### Async SQL Operations

The SQL CRUD interface also provides asynchronous methods for working with SQL databases, which are prefixed with 'a'.

```python
from keble_db.crud.sql import SqlCRUDBase
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from keble_db.schemas import QueryBase

# Define your model (same as for synchronous operations)
class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    email: str
    age: int

# Create a CRUD instance (same as for synchronous operations)
user_crud = SqlCRUDBase(
    model=User,
    table_name="users"
)

# Create an async session
# Note: Must use an async driver (psycopg for PostgreSQL, aiosqlite for SQLite)
engine = create_async_engine("postgresql+psycopg://user:password@localhost/dbname")
async with AsyncSession(engine) as session:
    # Create a document asynchronously
    user = User(name="John", email="john@example.com", age=30)
    # Returns the created User instance with populated id
    created_user = await user_crud.acreate(session, obj_in=user)
    
    # Create multiple documents asynchronously
    users = [
        User(name="Alice", email="alice@example.com", age=25),
        User(name="Bob", email="bob@example.com", age=35),
    ]
    # Returns a list of created User instances
    created_users = await user_crud.acreate_multi(session, obj_in_list=users)
    
    # SQL QueryBase usage (same as synchronous)
    query = QueryBase(
        # SQL uses list of SQLAlchemy expressions for filters
        filters=[User.age > 18, User.name == "John"],
        limit=10,
        offset=0,
        order_by=[User.created_at.desc()]  # List of SQLAlchemy expression objects
    )
    
    # Read documents asynchronously
    # Returns a User instance or None
    user = await user_crud.afirst(session, query=query)
    # Returns a list of User instances
    users = await user_crud.aget_multi(session, query=QueryBase(limit=10, offset=0))
    # SQL _id is typically a UUID or int depending on your model
    user_by_id = await user_crud.afirst_by_id(session, _id=uuid4())
    
    # Count documents asynchronously
    # Returns an integer
    count = await user_crud.acount(session, query=QueryBase(filters=[User.age > 18]))
    
    # Update a document asynchronously
    # Returns the updated User instance
    updated_user = await user_crud.aupdate(session, _id=uuid4(), obj_in={"age": 31})
    
    # Delete documents asynchronously
    # Returns None
    await user_crud.adelete(session, _id=uuid4())
    # Can delete by id or by object instances
    await user_crud.adelete_multi(session, obj_in_list=[uuid4(), user1, user2])
```

Using the database session manager:

```python
from keble_db.session import Db
from keble_db.schemas import DbSettingsABC
from sqlmodel.ext.asyncio.session import AsyncSession

# Initialize DB with settings
db = Db(settings)  # settings implements DbSettingsABC

# Get async SQL session
async_session = db.get_async_sql_write_client()

try:
    # Use the async session with the CRUD methods
    user = await user_crud.afirst(
        async_session, 
        query=QueryBase(filters=[User.name == "John"])
    )
    
    # Update the user
    if user:
        updated_user = await user_crud.aupdate(
            async_session,
            _id=user.id,
            obj_in={"age": 32}
        )
finally:
    # Always close the session
    await db.try_close_async(async_session)
```

With FastAPI dependency injection:

```python
from fastapi import FastAPI, Depends
from keble_db.deps.api import ApiDbDeps

# Initialize dependencies
api_db_deps = ApiDbDeps(db)
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    async_session = Depends(api_db_deps.get_async_read_sql)
):
    user = await user_crud.afirst_by_id(async_session, _id=user_id)
    return user

@app.post("/users")
async def create_user(
    user_data: UserCreate,
    async_session = Depends(api_db_deps.get_async_write_sql)
):
    user = User(**user_data.dict())
    created_user = await user_crud.acreate(async_session, obj_in=user)
    return created_user
```

### Qdrant Vector Database CRUD Operations

The Qdrant CRUD interface provides methods for working with Qdrant vector database.

```python
from keble_db.crud.qdrant import QdrantCRUDBase
from qdrant_client import QdrantClient, AsyncQdrantClient
from pydantic import BaseModel
from typing import List
from keble_db.schemas import QueryBase

# Define your models
class VectorModel(BaseModel):
    vector: List[float]

class Item(BaseModel):
    id: int
    name: str
    description: str

# Create a CRUD instance
item_crud = QdrantCRUDBase(
    model=Item,
    vector_model=VectorModel,
    collection="items"
)

# Synchronous operations
qdrant_client = QdrantClient("localhost", port=6333)

# Create an item with vector
vector = VectorModel(vector=[0.1, 0.2, 0.3])
item = Item(id=1, name="Test Item", description="This is a test item")
# Returns boolean (True if operation was successful)
result = item_crud.create(qdrant_client, vector, item, "unique_id_1")

# Create multiple items
items_and_vectors = [
    ("unique_id_2", Item(id=2, name="Item 2", description="Description 2"), VectorModel(vector=[0.4, 0.5, 0.6])),
    ("unique_id_3", Item(id=3, name="Item 3", description="Description 3"), VectorModel(vector=[0.7, 0.8, 0.9])),
]
# Returns boolean (True if operation was successful)
result = item_crud.create_multi(qdrant_client, payloads_and_vectors=items_and_vectors)

# Qdrant QueryBase usage
# order_by is not applicable for vector similarity search
query = QueryBase(
    filters={"name": {"$eq": "Test Item"}},  # Qdrant uses dict for filters
    limit=10,
    offset=0,  # For search: int offset
    # order_by is not applicable for Qdrant vector similarity search
)

# Read items
# Returns Item instance or None
item = item_crud.first_by_id(qdrant_client, _id="unique_id_1")
# Returns full Qdrant record (with vector and payload)
record = item_crud.first_record_by_id(qdrant_client, _id="unique_id_1")
# Returns list of Item instances
items = item_crud.get_multi_by_ids(qdrant_client, _ids=["unique_id_1", "unique_id_2"])
# Returns list of full Qdrant records
records = item_crud.get_multi_records_by_ids(qdrant_client, _ids=["unique_id_1", "unique_id_2"])

# Search by vector similarity
# Returns list of search results with scores
search_results = item_crud.search(
    qdrant_client,
    vector=[0.1, 0.2, 0.3],
    vector_key="vector",
    score_threshold=0.75
)

# Update items
# Returns boolean (True if operation was successful)
result = item_crud.update_payload(qdrant_client, _id="unique_id_1", payload=item)
result = item_crud.overwrite_payload(qdrant_client, _id="unique_id_1", payload=item)
result = item_crud.update_vector(qdrant_client, _id="unique_id_1", vector=vector)

# Delete items
# Returns boolean (True if operation was successful)
result = item_crud.delete(qdrant_client, _id="unique_id_1")
result = item_crud.delete_multi(qdrant_client, query=QueryBase(filters={"name": {"$eq": "Test Item"}}))

# Scroll through items with pagination using point_id
# Returns tuple of (list of items, next_point_id)
items, next_point_id = item_crud.scroll(
    qdrant_client,
    query=QueryBase(
        filters={"name": {"$eq": "Test Item"}},
        limit=10,
        offset=None  # First page has None offset, subsequent pages use the returned next_point_id
    )
)
# Using the next_point_id for the next page
if next_point_id:
    next_page_items, next_point_id = item_crud.scroll(
        qdrant_client,
        query=QueryBase(
            filters={"name": {"$eq": "Test Item"}},
            limit=10,
            offset=next_point_id  # Use the point_id as string offset
        )
    )

# Asynchronous operations
async_qdrant_client = AsyncQdrantClient("localhost", port=6333)

# Create an item asynchronously
result = await item_crud.acreate(async_qdrant_client, vector, item, "unique_id_4")

# Read items asynchronously
item = await item_crud.afirst_by_id(async_qdrant_client, _id="unique_id_4")
items = await item_crud.aget_multi_by_ids(async_qdrant_client, _ids=["unique_id_4"])

# Search asynchronously
search_results = await item_crud.asearch(
    async_qdrant_client,
    vector=[0.1, 0.2, 0.3],
    vector_key="vector",
    score_threshold=0.75
)

# Update items asynchronously
await item_crud.aupdate_payload(async_qdrant_client, _id="unique_id_4", payload=item)
await item_crud.aoverwrite_payload(async_qdrant_client, _id="unique_id_4", payload=item)
await item_crud.aupdate_vector(async_qdrant_client, _id="unique_id_4", vector=vector)

# Delete items asynchronously
await item_crud.adelete(async_qdrant_client, _id="unique_id_4")
await item_crud.adelete_multi(async_qdrant_client, query=QueryBase(filters={"name": {"$eq": "Test Item"}}))

# Scroll items asynchronously
items, next_point_id = await item_crud.ascroll(
    async_qdrant_client,
    query=QueryBase(
        filters={"name": {"$eq": "Test Item"}},
        limit=10
    )
)
```

## Database Session Management

The `session` module provides tools for managing database connections in API services. It handles the creation and management of database sessions, which should be handled at the API endpoint level.

```python
from keble_db import DbSettingsABC
from pydantic_settings import BaseSettings
from fastapi import FastAPI, Depends

# 1. Define settings class implementing the DbSettingsABC interface
class Settings(BaseSettings, DbSettingsABC):
    # Implement required settings for database connections
    mongodb_uri: str
    sql_uri: str
    async_sql_uri: str  # For async SQL connections
    redis_url: str
    # ... other settings
    
# 2. Initialize settings
settings = Settings()

# 3. Initialize database and dependency objects
from keble_db.session import Db
from keble_db.deps.api import ApiDbDeps

# Initialize the core database handler
db = Db(settings)

# Example of db usage
mongo_client = db.get_mongo()
redis_client = db.get_redis(namespace="my-app")
sql_session = db.get_sql_write_client()

# Async SQL usage
async_sql_session = db.get_async_sql_write_client()  # Returns SQLModelAsyncSession
# Use async_sql_session in async methods with await

# Initialize the API dependencies handler
api_db_deps = ApiDbDeps(db)

# 4. Use in FastAPI application
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: str, mongo_client = Depends(api_db_deps.get_amongo)):
    # Use the mongo client to access the database
    user = await user_crud.afirst_by_id(mongo_client, _id=user_id)
    return user

@app.get("/products")
def get_products(sql_session = Depends(api_db_deps.get_read_sql)):
    # Use SQL session (synchronous)
    products = product_crud.get_multi(sql_session, query=QueryBase(limit=10))
    return products

@app.get("/products-async")
async def get_products_async(async_sql_session = Depends(api_db_deps.get_async_read_sql)):
    # Use async SQL session (asynchronous)
    products = await product_crud.aget_multi(async_sql_session, query=QueryBase(limit=10))
    return products

@app.get("/cache")
def get_cache(redis_client = Depends(api_db_deps.get_redis)):
    # Use Redis client
    cached_data = redis_client.get("some_key")
    return {"data": cached_data}

@app.get("/cache-async")
async def get_cache_async(redis_client = Depends(api_db_deps.get_aredis)):
    # Use async Redis client
    cached_data = await redis_client.get("some_key")
    return {"data": cached_data}

@app.get("/namespaced-cache")
def get_namespaced_cache(redis_client = Depends(lambda: api_db_deps.get_extended_redis(namespace="my-namespace"))):
    # Use extended Redis client with namespace
    cached_data = redis_client.get("some_key")  # Will be prefixed with "my-namespace:"
    return {"data": cached_data}

@app.get("/namespaced-cache-async")
async def get_namespaced_cache_async(redis_client = Depends(lambda: api_db_deps.get_extended_aredis(namespace="my-namespace"))):
    # Use extended async Redis client with namespace
    cached_data = await redis_client.get("some_key")  # Will be prefixed with "my-namespace:"
    return {"data": cached_data}
```

### FastAPI Dependency Injection

The `ApiDbDeps` class provides dependency injection for FastAPI applications, handling the lifecycle of database connections:

| Dependency Method | Return Type | Description |
|-------------------|-------------|-------------|
| `get_redis()` | `Redis \| None` | Synchronous Redis client with proper connection lifecycle |
| `get_aredis()` | `AsyncRedis` | Asynchronous Redis client |
| `get_extended_redis(namespace=None)` | `ExtendedRedis \| None` | Extended Redis client with namespace support |
| `get_extended_aredis(namespace=None)` | `ExtendedAsyncRedis \| None` | Extended asynchronous Redis client with namespace support |
| `get_mongo()` | `MongoClient \| None` | Synchronous MongoDB client |
| `get_amongo()` | `AsyncIOMotorClient` | Asynchronous MongoDB client |
| `get_write_sql()` | `Session \| None` | Synchronous SQL session for write operations |
| `get_read_sql()` | `Session \| None` | Synchronous SQL session for read operations |
| `get_async_write_sql()` | `SQLModelAsyncSession \| None` | Asynchronous SQL session for write operations |
| `get_async_read_sql()` | `SQLModelAsyncSession \| None` | Asynchronous SQL session for read operations |
| `get_qdrant()` | `QdrantClient \| None` | Synchronous Qdrant client |
| `get_aqdrant()` | `AsyncQdrantClient \| None` | Asynchronous Qdrant client |

Each dependency method creates a new client instance and manages its lifecycle, ensuring connections are properly closed after the API request completes.

#### Extended Redis Functionality

The extended Redis clients (`ExtendedRedis` and `ExtendedAsyncRedis`) provide additional functionality:

- **Namespace support**: Automatically prefixes all keys with the namespace
- **Batch operations**: Methods for efficient batch retrieval and storage
- **Type conversion**: Automatic serialization/deserialization of values

Example with namespace:

```python
# Get extended Redis client
extended_redis = api_db_deps.get_extended_redis(namespace="my-app")

# Key will be stored as "my-app:user:123"
extended_redis.set("user:123", json.dumps({"name": "John"}))

# Retrieves from "my-app:user:123"
value = extended_redis.get("user:123")
```

### Async Database Connections

All async connections in keble-db follow the same pattern - the methods are prefixed with 'a' to indicate they're async:

| Synchronous Method | Async Method | Description |
|--------------------|--------------|-------------|
| `get_mongo()` | `get_amongo()` | MongoDB client |
| `get_redis()` | `get_aredis()` | Redis client |
| `get_qdrant_client()` | `get_aqdrant_client()` | Qdrant client |
| `get_sql_write_client()` | `get_async_sql_write_client()` | SQL write client |
| `get_sql_read_client()` | `get_async_sql_read_client()` | SQL read client |

For FastAPI dependency injection, use the corresponding methods from `ApiDbDeps`:

| Synchronous Dependency | Async Dependency | Description |
|-----------------------|------------------|-------------|
| `get_mongo()` | `get_amongo()` | MongoDB client |
| `get_redis()` | `get_aredis()` | Redis client |
| `get_qdrant()` | `get_aqdrant()` | Qdrant client |
| `get_write_sql()` | `get_async_write_sql()` | SQL write client |
| `get_read_sql()` | `get_async_read_sql()` | SQL read client |

#### Async SQL Configuration

For async SQL support, you need to configure your database settings:

##### PostgreSQL with Psycopg v3 (Recommended)

Psycopg v3 is the recommended PostgreSQL driver for both synchronous and asynchronous operations:

```bash
# Install Psycopg v3 with binary and connection pooling support
poetry add 'psycopg[binary,pool]>=3.1.10' psycopg-pool greenlet

# If upgrading from psycopg2, remove it first
poetry remove psycopg2 psycopg2-binary
```

Configure your connection strings:

```python
# In your settings class
class Settings(BaseSettings, DbSettingsABC):
    # Synchronous SQL connection with Psycopg v3
    sql_uri: str = "postgresql+psycopg://user:password@localhost:5432/dbname"
    
    # Async SQL connection with Psycopg v3 (same format as sync!)
    async_sql_uri: str = "postgresql+psycopg://user:password@localhost:5432/dbname"
    
    # You can also specify separate read connections
    sql_read_uri: Optional[str] = None  # If None, sql_uri is used for both
    async_sql_read_uri: Optional[str] = None  # If None, async_sql_uri is used for both
    
    # Connection arguments (optional)
    @property
    def sql_connect_args(self) -> Dict[str, Any]:
        return {
            "application_name": "my_app",
            "connect_timeout": 10,
            # Other Psycopg3 connection parameters
        }
```

Important notes on using Psycopg v3:
- Use `postgresql+psycopg` for both sync and async connections (not the older `postgresql+asyncpg`)
- Psycopg v3 supports both synchronous and asynchronous operations with the same driver
- The async functionality is handled automatically by SQLAlchemy
- Always include the port (`:5432`) in your connection strings for better reliability
- Make sure to have `greenlet` installed: `poetry add greenlet`

##### Other Database Drivers

For other databases, install the appropriate async driver:
- For PostgreSQL with asyncpg: `poetry add asyncpg` and use `postgresql+asyncpg://user:password@localhost/dbname` 
- For SQLite: `poetry add aiosqlite` and use `sqlite+aiosqlite:///database.db`
- For MySQL: `poetry add aiomysql` and use `mysql+aiomysql://user:password@localhost/dbname`

Always properly close async SQL sessions:
```python
try:
    # Use async_session
    result = await crud.afirst(async_session, query=query)
finally:
    await db.try_close_async(async_session)
```

## Extended Redis Support

The package provides extended Redis functionality with namespace management and batch operations.

```python
from keble_db.wrapper import ExtendedRedis
from redis import Redis

redis_client = Redis(host="localhost", port=6379)
# The ExtendedRedis act like redis.asyncio.Redis,
# which it DOES NOT have an "a" in front of the api,
# but all apis are awaitable
extended_redis = ExtendedRedis(redis_client, namespace="my-app")

# Set with namespace
await extended_redis.set("user:1", "data")  # Actual key: "my-app:user:1"

# Get with namespace
data = await extended_redis.get("user:1")

# Delete all keys in a namespace
await extended_redis.delete_keys_by_pattern("user:*")  # Deletes all "my-app:user:*" keys
```
