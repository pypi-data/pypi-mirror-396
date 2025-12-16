# Best Practices

This guide covers recommended patterns and practices when building applications with Tachyon Engine.

## Project Structure

### Recommended Layout

```
my_project/
├── app/
│   ├── __init__.py
│   ├── main.py          # Application entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── posts.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── post.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py
│   └── config.py
├── tests/
│   ├── test_users.py
│   └── test_posts.py
├── requirements.txt
└── README.md
```

## Application Design

### Single Responsibility

Keep route handlers focused and single-purpose:

```python
# ✅ Good - focused handler
async def get_user(request: Request):
    user_id = request.path_params.get("user_id")
    user = await fetch_user(user_id)
    return JSONResponse(user)

# ❌ Bad - doing too much
async def get_user(request: Request):
    user_id = request.path_params.get("user_id")
    # Validate
    # Fetch from DB
    # Transform data
    # Log
    # Send notification
    # etc...
```

### Separate Concerns

```python
# models/user.py
class UserModel:
    @staticmethod
    async def get(user_id: int):
        # Database logic
        pass

# routes/users.py
from app.models.user import UserModel

async def get_user(request: Request):
    user_id = request.path_params.get("user_id")
    user = await UserModel.get(user_id)
    return JSONResponse(user)
```

## Performance Optimization

### Reuse Application Instance

```python
# ✅ Good - single instance
app = TachyonEngine()

# Define all routes
app.add_route(Route("/users", get_users))
app.add_route(Route("/posts", get_posts))

# ❌ Bad - creating multiple instances
def create_app():
    return TachyonEngine()  # Don't do this repeatedly
```

### Minimize Route Creation

```python
# ✅ Good - create routes once at startup
routes = [
    Route("/users", get_users),
    Route("/posts", get_posts),
]

for route in routes:
    app.add_route(route)

# ❌ Bad - creating routes in request handlers
async def handler(request):
    # Don't create routes here!
    pass
```

### Use Appropriate Data Structures

```python
# ✅ Good - efficient header access
auth = request.headers.get("authorization")

# ❌ Bad - accessing through dict conversion
headers_dict = dict(request.headers.items())
auth = headers_dict.get("authorization")
```

## Error Handling

### Centralized Error Handling

```python
class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

async def error_handler(request: Request, exc: Exception):
    if isinstance(exc, APIError):
        return JSONResponse({
            "error": exc.message
        }, status_code=exc.status_code)
    
    return JSONResponse({
        "error": "Internal server error"
    }, status_code=500)
```

### Specific Exception Handling

```python
async def get_user(request: Request):
    try:
        user_id = int(request.path_params.get("user_id"))
    except (ValueError, TypeError):
        return JSONResponse({
            "error": "Invalid user ID"
        }, status_code=400)
    
    try:
        user = await fetch_user(user_id)
    except UserNotFound:
        return JSONResponse({
            "error": "User not found"
        }, status_code=404)
    
    return JSONResponse(user)
```

## Request Validation

### Input Validation

```python
from typing import Optional
from pydantic import BaseModel, validator

class CreateUserRequest(BaseModel):
    username: str
    email: str
    age: Optional[int] = None
    
    @validator('username')
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username too short')
        return v

async def create_user(request: Request):
    try:
        data = request.json()
        user_data = CreateUserRequest(**data)
        # Process validated data
        return JSONResponse({"created": True})
    except ValidationError as e:
        return JSONResponse({
            "error": "Validation failed",
            "details": e.errors()
        }, status_code=400)
```

## Security Best Practices

### Authentication

```python
async def require_auth(request: Request):
    """Middleware to check authentication"""
    token = request.headers.get("authorization")
    
    if not token:
        return JSONResponse({
            "error": "Authentication required"
        }, status_code=401)
    
    try:
        user = verify_token(token)
        request.set_state("user", user)
    except InvalidToken:
        return JSONResponse({
            "error": "Invalid token"
        }, status_code=401)
```

### Input Sanitization

```python
import re

def sanitize_input(text: str) -> str:
    """Remove potentially dangerous characters"""
    return re.sub(r'[<>\"\'&]', '', text)

async def create_post(request: Request):
    data = request.json()
    title = sanitize_input(data.get("title", ""))
    content = sanitize_input(data.get("content", ""))
    # Process sanitized data
```

### CORS Headers

```python
def add_cors_headers(response: Response) -> Response:
    response.set_header("Access-Control-Allow-Origin", "*")
    response.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
    response.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response
```

## Testing

### Unit Testing

```python
import pytest
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

@pytest.fixture
def app():
    app = TachyonEngine()
    
    async def test_handler(request: Request):
        return JSONResponse({"test": True})
    
    app.add_route(Route("/test", test_handler))
    return app

def test_route_exists(app):
    assert len(app.routes) == 1
    assert app.routes[0].path == "/test"
```

### Integration Testing

```python
from tachyon_engine import TestClient

def test_api_endpoint():
    app = create_app()
    client = TestClient(app)
    
    response = client.get("/users/1")
    assert response.status_code == 200
    # Note: Full TestClient implementation pending
```

## Logging

### Structured Logging

```python
import logging
import json

logger = logging.getLogger(__name__)

async def log_request(request: Request):
    logger.info(json.dumps({
        "method": request.method,
        "path": request.path,
        "query_params": dict(request.query_params.items()),
        "user_agent": request.headers.get("user-agent")
    }))
```

### Performance Logging

```python
import time

async def timed_handler(request: Request):
    start = time.time()
    
    response = await actual_handler(request)
    
    duration = time.time() - start
    logger.info(f"Request took {duration:.3f}s")
    
    return response
```

## Configuration Management

### Environment Variables

```python
import os

class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set")

app = TachyonEngine(debug=Config.DEBUG)
```

### Configuration File

```python
# config.py
from dataclasses import dataclass

@dataclass
class AppConfig:
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

config = AppConfig()
```

## Async Best Practices

### Use Async Consistently

```python
# ✅ Good - proper async
async def get_users(request: Request):
    users = await db.fetch_users()
    return JSONResponse(users)

# ❌ Bad - blocking in async
async def get_users(request: Request):
    users = db.fetch_users_sync()  # Blocks event loop!
    return JSONResponse(users)
```

### Concurrent Operations

```python
import asyncio

async def get_dashboard(request: Request):
    # Fetch multiple resources concurrently
    users, posts, stats = await asyncio.gather(
        fetch_users(),
        fetch_posts(),
        fetch_stats()
    )
    
    return JSONResponse({
        "users": users,
        "posts": posts,
        "stats": stats
    })
```

## Documentation

### Route Documentation

```python
async def get_user(request: Request):
    """
    Get user by ID
    
    Args:
        request: Request object containing user_id in path params
    
    Returns:
        JSONResponse with user data or 404 if not found
    
    Example:
        GET /users/123
        Response: {"id": 123, "name": "John"}
    """
    user_id = request.path_params.get("user_id")
    # Implementation
```

### API Documentation

Consider using tools like:
- OpenAPI/Swagger
- ReDoc
- Postman collections

## Deployment

### Production Checklist

- [ ] Set `debug=False`
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Set up logging
- [ ] Configure error monitoring
- [ ] Set up health checks
- [ ] Use a reverse proxy (nginx/caddy)
- [ ] Enable compression
- [ ] Set appropriate CORS headers
- [ ] Rate limiting
- [ ] Load balancing

### Health Check Endpoint

```python
async def health_check(request: Request):
    return JSONResponse({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    })

app.add_route(Route("/health", health_check, methods=["GET"]))
```

## Performance Monitoring

```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.requests = []
    
    async def track_request(self, request: Request):
        start = time.time()
        response = await next_handler(request)
        duration = time.time() - start
        
        self.requests.append({
            "path": request.path,
            "method": request.method,
            "duration": duration,
            "timestamp": start
        })
        
        return response
```

---

Next: Learn about the [Architecture](architecture.md) of Tachyon Engine

