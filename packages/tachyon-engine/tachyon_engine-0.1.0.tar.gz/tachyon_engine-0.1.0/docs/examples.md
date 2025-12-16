# Examples

Real-world examples of using Tachyon Engine.

## Basic REST API

```python
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

app = TachyonEngine()

# In-memory database
users_db = {}
next_id = 1

async def list_users(request: Request):
    """GET /users - List all users"""
    return JSONResponse({"users": list(users_db.values())})

async def get_user(request: Request):
    """GET /users/{user_id} - Get user by ID"""
    user_id = request.path_params.get("user_id")
    
    if user_id not in users_db:
        return JSONResponse(
            {"error": "User not found"},
            status_code=404
        )
    
    return JSONResponse({"user": users_db[user_id]})

async def create_user(request: Request):
    """POST /users - Create new user"""
    global next_id
    
    try:
        data = request.json()
        user = {
            "id": next_id,
            "name": data.get("name"),
            "email": data.get("email"),
        }
        users_db[str(next_id)] = user
        next_id += 1
        
        return JSONResponse(user, status_code=201)
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=400
        )

async def update_user(request: Request):
    """PUT /users/{user_id} - Update user"""
    user_id = request.path_params.get("user_id")
    
    if user_id not in users_db:
        return JSONResponse(
            {"error": "User not found"},
            status_code=404
        )
    
    data = request.json()
    users_db[user_id].update(data)
    
    return JSONResponse({"user": users_db[user_id]})

async def delete_user(request: Request):
    """DELETE /users/{user_id} - Delete user"""
    user_id = request.path_params.get("user_id")
    
    if user_id not in users_db:
        return JSONResponse(
            {"error": "User not found"},
            status_code=404
        )
    
    del users_db[user_id]
    return JSONResponse({"deleted": True}, status_code=204)

# Register routes
app.add_route(Route("/users", list_users, methods=["GET"]))
app.add_route(Route("/users", create_user, methods=["POST"]))
app.add_route(Route("/users/{user_id}", get_user, methods=["GET"]))
app.add_route(Route("/users/{user_id}", update_user, methods=["PUT"]))
app.add_route(Route("/users/{user_id}", delete_user, methods=["DELETE"]))
```

## Authentication

```python
from functools import wraps

# Simple token storage (use a real database in production!)
valid_tokens = {"secret123": "user1", "secret456": "user2"}

def require_auth(handler):
    """Decorator to require authentication"""
    @wraps(handler)
    async def wrapper(request: Request):
        auth_header = request.headers.get("authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                {"error": "Authentication required"},
                status_code=401
            )
        
        token = auth_header.split(" ")[1]
        
        if token not in valid_tokens:
            return JSONResponse(
                {"error": "Invalid token"},
                status_code=401
            )
        
        # Set user in request state
        request.set_state("user_id", valid_tokens[token])
        
        return await handler(request)
    
    return wrapper

@require_auth
async def protected_endpoint(request: Request):
    user_id = request.state.get("user_id")
    return JSONResponse({
        "message": "Protected data",
        "user_id": user_id
    })

app.add_route(Route("/protected", protected_endpoint, methods=["GET"]))
```

## File Upload

```python
async def upload_file(request: Request):
    """Handle file upload"""
    form = request.form()
    file = form.get("file")
    
    if not isinstance(file, UploadFile):
        return JSONResponse(
            {"error": "No file provided"},
            status_code=400
        )
    
    # Save file
    filepath = f"/uploads/{file.filename}"
    file.save(filepath)
    
    return JSONResponse({
        "filename": file.filename,
        "size": file.size,
        "content_type": file.content_type,
        "saved_to": filepath
    })

app.add_route(Route("/upload", upload_file, methods=["POST"]))
```

## Pagination

```python
async def paginated_list(request: Request):
    """GET /items?page=1&per_page=10"""
    try:
        page = int(request.query_params.get("page") or "1")
        per_page = int(request.query_params.get("per_page") or "10")
    except ValueError:
        return JSONResponse(
            {"error": "Invalid pagination parameters"},
            status_code=400
        )
    
    # Simulate database query
    all_items = list(range(1, 101))  # 100 items
    start = (page - 1) * per_page
    end = start + per_page
    items = all_items[start:end]
    
    return JSONResponse({
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": len(all_items),
        "total_pages": (len(all_items) + per_page - 1) // per_page
    })

app.add_route(Route("/items", paginated_list, methods=["GET"]))
```

## Error Handling

```python
class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

async def safe_endpoint(request: Request):
    try:
        # Your logic here
        user_id = request.path_params.get("user_id")
        
        if not user_id.isdigit():
            raise APIError("Invalid user ID", 400)
        
        user_id_int = int(user_id)
        
        if user_id_int > 1000:
            raise APIError("User not found", 404)
        
        return JSONResponse({"user_id": user_id_int})
        
    except APIError as e:
        return JSONResponse(
            {"error": e.message},
            status_code=e.status_code
        )
    except Exception as e:
        return JSONResponse(
            {"error": "Internal server error"},
            status_code=500
        )

app.add_route(Route("/users/{user_id}", safe_endpoint, methods=["GET"]))
```

## WebSocket Chat

```python
from tachyon_engine import WebSocketRoute, WebSocket

# Store active connections
active_connections = []

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket chat endpoint"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_json()
            
            # Broadcast to all connections
            for connection in active_connections:
                await connection.send_json({
                    "message": message,
                    "clients": len(active_connections)
                })
    
    except Exception:
        pass
    finally:
        active_connections.remove(websocket)
        await websocket.close()

app.add_route(WebSocketRoute("/ws/chat", websocket_endpoint))
```

## Middleware Chain

```python
import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            logger.info(f"{scope['method']} {scope['path']}")
        await self.app(scope, receive, send)

class TimingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        start = time.time()
        await self.app(scope, receive, send)
        duration = time.time() - start
        logger.info(f"Request completed in {duration:.3f}s")

class CORSMiddleware:
    def __init__(self, app, allow_origins=None):
        self.app = app
        self.allow_origins = allow_origins or ["*"]
    
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append((b"access-control-allow-origin", b"*"))
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

# Add middleware (LIFO order)
app.add_middleware(Middleware(LoggingMiddleware))
app.add_middleware(Middleware(TimingMiddleware))
app.add_middleware(Middleware(CORSMiddleware, allow_origins=["*"]))
```

## Health Check

```python
async def health_check(request: Request):
    """GET /health - Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    })

app.add_route(Route("/health", health_check, methods=["GET"]))
```

## Search API

```python
async def search(request: Request):
    """GET /search?q=query&filter=type"""
    query = request.query_params.get("q")
    filter_type = request.query_params.get("filter")
    
    if not query:
        return JSONResponse(
            {"error": "Query parameter 'q' is required"},
            status_code=400
        )
    
    # Simulate search
    results = [
        {"id": 1, "title": f"Result for {query}"},
        {"id": 2, "title": f"Another result for {query}"},
    ]
    
    if filter_type:
        results = [r for r in results if filter_type in r["title"]]
    
    return JSONResponse({
        "query": query,
        "filter": filter_type,
        "results": results,
        "count": len(results)
    })

app.add_route(Route("/search", search, methods=["GET"]))
```

## Complete CRUD Application

See [`examples/simple_app.py`](../examples/simple_app.py) for a complete working example.

## Testing

```python
from tachyon_engine import TestClient

def test_api():
    app = TachyonEngine()
    
    async def handler(request: Request):
        return JSONResponse({"test": True})
    
    app.add_route(Route("/test", handler))
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert response.status_code == 200
    # Full implementation pending
```

---

More examples coming soon! Check the [`examples/`](../examples/) directory for working code.

