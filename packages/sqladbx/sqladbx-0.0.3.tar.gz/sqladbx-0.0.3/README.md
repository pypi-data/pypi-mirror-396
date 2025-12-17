# sqladbx 🚀

Modern async SQLAlchemy database context manager for **FastAPI**, **Litestar**, **Taskiq**, **Temporal**, and more.

[![PyPI version](https://badge.fury.io/py/sqladbx.svg)](https://badge.fury.io/py/sqladbx)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎯 **Simple API** - Clean, intuitive interface for database operations
- ⚡ **Async-first** - Built for async/await with SQLAlchemy 2.0+
- 🔄 **Auto Context Management** - Automatic session lifecycle with middleware
- 🌐 **Framework Agnostic** - Works with FastAPI, Litestar, Starlette, and more
- 🎭 **Multi-Session Support** - Handle multiple concurrent sessions when needed
- 🔒 **Type Safe** - Full type hints and mypy support
- 🧪 **Well Tested** - Comprehensive test coverage

## 📦 Installation

```bash
pip install sqladbx
```

For development with all test dependencies:

```bash
pip install sqladbx[test]
```

## 🚀 Quick Start

### FastAPI Example

```python
from fastapi import FastAPI
from sqlmodel import Field, SQLModel
from sqladbx import SQLAlchemyMiddleware, db

# Define your model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str

# Create FastAPI app
app = FastAPI()

# Add SQLAlchemy middleware
app.add_middleware(
    SQLAlchemyMiddleware,
    db_url="postgresql+asyncpg://user:password@localhost/dbname"
)

# Use db.session in your endpoints - no context manager needed!
@app.post("/users")
async def create_user(name: str, email: str):
    user = User(name=name, email=email)
    db.session.add(user)
    await db.session.commit()
    await db.session.refresh(user)
    return user

@app.get("/users")
async def list_users():
    result = await db.session.execute(select(User))
    return result.scalars().all()
```

### Litestar Example

```python
from litestar import Litestar, get, post
from litestar.middleware import DefineMiddleware
from sqlmodel import Field, SQLModel
from sqladbx import SQLAlchemyMiddleware, db

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    price: float

@post("/products")
async def create_product(name: str, price: float) -> Product:
    product = Product(name=name, price=price)
    db.session.add(product)
    await db.session.commit()
    await db.session.refresh(product)
    return product

@get("/products")
async def list_products() -> list[Product]:
    result = await db.session.execute(select(Product))
    return result.scalars().all()

app = Litestar(
    route_handlers=[create_product, list_products],
    middleware=[
        DefineMiddleware(
            SQLAlchemyMiddleware,
            db_url="postgresql+asyncpg://user:password@localhost/dbname"
        )
    ],
)
```

## 🎯 Core Concepts

### 1️⃣ Automatic Session Management

With middleware, sessions are automatically managed per request:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # Session is automatically available
    user = await db.session.get(User, user_id)
    return user
    # Session is automatically committed and closed
```

### 2️⃣ Manual Context Management

For non-web contexts (CLI, background tasks, etc.):

```python
from sqladbx import DBProxy

db = DBProxy()
db.initialize(db_url="postgresql+asyncpg://user:password@localhost/dbname")

async def process_data():
    async with db():
        user = User(name="John", email="john@example.com")
        db.session.add(user)
        await db.session.commit()
```

### 3️⃣ Multi-Session Mode

For complex scenarios requiring multiple concurrent sessions:

```python
async def complex_operation():
    async with db(multi_sessions=True):
        # Each call creates a new session
        session1 = db.session  # First session
        session2 = db.session  # Second session (independent)

        # Both sessions are tracked and cleaned up automatically
```

### 4️⃣ Auto-Commit Mode

Enable automatic commit on context exit:

```python
async with db(commit_on_exit=True):
    user = User(name="Jane", email="jane@example.com")
    db.session.add(user)
    # Automatically commits on exit
```

## 🔧 Advanced Usage

### Master-Replica Setup

```python
from sqladbx import DBProxy, create_db_middleware

# Create separate proxies for master and replica
master_db = DBProxy()
replica_db = DBProxy()

# Create custom middleware classes
MasterMiddleware = create_db_middleware(master_db)
ReplicaMiddleware = create_db_middleware(replica_db)

app = FastAPI()

# Add both middlewares
app.add_middleware(
    MasterMiddleware,
    db_url="postgresql+asyncpg://user:pass@master/db"
)
app.add_middleware(
    ReplicaMiddleware,
    db_url="postgresql+asyncpg://user:pass@replica/db"
)

@app.post("/users")
async def create_user(name: str):
    # Write to master
    user = User(name=name)
    master_db.session.add(user)
    await master_db.session.commit()
    return user

@app.get("/users")
async def list_users():
    # Read from replica
    result = await replica_db.session.execute(select(User))
    return result.scalars().all()
```

### Custom Engine Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine

# Create custom engine with specific settings
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    echo=True,  # SQL logging
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Use custom engine with middleware
app.add_middleware(
    SQLAlchemyMiddleware,
    custom_engine=engine
)
```

### Taskiq Integration

```python
from taskiq import TaskiqScheduler, TaskiqWorker
from sqladbx import DBProxy

db = DBProxy()
db.initialize(db_url="postgresql+asyncpg://user:pass@localhost/db")

@broker.task
async def process_user(user_id: int):
    async with db():
        user = await db.session.get(User, user_id)
        # Process user
        await db.session.commit()
```

### Temporal Workflow

```python
from temporalio import workflow
from sqladbx import DBProxy

db = DBProxy()
db.initialize(db_url="postgresql+asyncpg://user:pass@localhost/db")

@workflow.defn
class UserWorkflow:
    @workflow.run
    async def run(self, user_id: int):
        async with db():
            user = await db.session.get(User, user_id)
            # Process user
            await db.session.commit()
```

## 🔒 Transaction Control

### Manual Transactions

```python
@app.post("/transfer")
async def transfer_money(from_id: int, to_id: int, amount: float):
    try:
        # Get accounts
        from_account = await db.session.get(Account, from_id)
        to_account = await db.session.get(Account, to_id)

        # Update balances
        from_account.balance -= amount
        to_account.balance += amount

        # Commit transaction
        await db.session.commit()
        return {"status": "success"}
    except Exception:
        # Rollback on error
        await db.session.rollback()
        raise
```

### Nested Transactions (Savepoints)

```python
async with db():
    # Main transaction
    user = User(name="John")
    db.session.add(user)

    async with db.session.begin_nested():
        # Nested transaction (savepoint)
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        # Can rollback to this savepoint if needed
```

## 🧪 Testing

```python
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine

@pytest.fixture
async def app():
    # Create test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Create app with test database
    app = FastAPI()
    app.add_middleware(
        SQLAlchemyMiddleware,
        custom_engine=engine
    )

    yield app

    await engine.dispose()

@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/users",
        params={"name": "John", "email": "john@example.com"}
    )
    assert response.status_code == 201
```

## ⚙️ Configuration

### Environment Variables

```bash
# Database URL
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# SQLAlchemy settings
DB_ECHO=true
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

### Configuration in Code

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "5")),
)

app.add_middleware(SQLAlchemyMiddleware, custom_engine=engine)
```

## 🎓 Best Practices

### ✅ DO

- Use middleware for web applications (automatic session management)
- Use manual context (`async with db()`) for CLI/background tasks
- Enable `commit_on_exit=True` for simple CRUD operations
- Use separate db proxies for master/replica setups
- Implement proper error handling with try/except

### ❌ DON'T

- Don't mix middleware and manual initialization
- Don't create sessions manually - use `db.session`
- Don't forget to handle exceptions in transactions
- Don't use blocking I/O inside database contexts
- Don't share sessions between requests

## 📊 Performance Tips

1. **Connection Pooling**: Configure appropriate pool size
   ```python
   engine = create_async_engine(url, pool_size=20, max_overflow=10)
   ```

2. **Batch Operations**: Use bulk operations for multiple inserts
   ```python
   db.session.add_all([User(name=f"User{i}") for i in range(100)])
   ```

3. **Lazy Loading**: Use `selectinload` for relationships
   ```python
   result = await db.session.execute(
       select(User).options(selectinload(User.posts))
   )
   ```

4. **Read Replicas**: Route read queries to replicas
   ```python
   # Write to master
   master_db.session.add(user)

   # Read from replica
   users = await replica_db.session.execute(select(User))
   ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI**: https://pypi.org/project/sqladbx/
- **GitHub**: https://github.com/your-org/sqladbx
- **Documentation**: https://github.com/your-org/sqladbx#readme
- **Issues**: https://github.com/your-org/sqladbx/issues

## 💬 Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Check existing issues and discussions
- Read the documentation carefully

---

Made with ❤️ by [Oleksii Svichkar](https://github.com/your-org)
