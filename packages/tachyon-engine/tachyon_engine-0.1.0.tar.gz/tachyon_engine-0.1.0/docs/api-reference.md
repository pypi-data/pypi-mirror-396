# API Reference

Complete API documentation for Tachyon Engine.

## TachyonEngine

Main application class.

### Constructor

```python
TachyonEngine(debug: bool = False, lifespan: Optional[Callable] = None)
```

**Parameters:**
- `debug` (bool): Enable debug mode
- `lifespan` (Callable): Lifespan context manager for startup/shutdown events

**Example:**
```python
app = TachyonEngine(debug=True)
```

### Methods

#### add_route

```python
add_route(route: Route) -> None
```

Add a route to the application.

**Parameters:**
- `route` (Route): Route object to add

**Example:**
```python
async def handler(request):
    return JSONResponse({"status": "ok"})

route = Route("/api/status", handler, methods=["GET"])
app.add_route(route)
```

#### add_middleware

```python
add_middleware(middleware: Middleware) -> None
```

Add middleware to the application stack.

**Parameters:**
- `middleware` (Middleware): Middleware instance

#### build_middleware_stack

```python
build_middleware_stack(app: Any) -> Any
```

Build the middleware stack (LIFO order).

#### run

```python
run(host: str = "127.0.0.1", port: int = 8000) -> None
```

Start the HTTP server.

**Parameters:**
- `host` (str): Host address
- `port` (int): Port number

### Attributes

- `routes` (List[Route]): List of registered routes
- `state` (Dict[str, Any]): Application-wide state dictionary

---

## Request

HTTP request object.

### Attributes

- `method` (str): HTTP method (GET, POST, etc.)
- `url` (str): Full URL
- `path` (str): URL path
- `headers` (Headers): Request headers
- `query_params` (QueryParams): Query parameters
- `path_params` (Dict[str, str]): Path parameters
- `cookies` (Dict[str, str]): Cookies
- `state` (Dict[str, Any]): Per-request state

### Methods

#### body

```python
body() -> bytes
```

Get the raw request body.

**Returns:** bytes

#### json

```python
json() -> Any
```

Parse request body as JSON.

**Returns:** Parsed JSON object (dict, list, etc.)

**Raises:** ValueError if body is not valid JSON

**Example:**
```python
async def create_user(request: Request):
    data = request.json()
    username = data.get("username")
    # ...
```

#### form

```python
form() -> Dict[str, Any]
```

Parse request body as form data.

**Returns:** Dict of form fields

**Supported content types:**
- `application/x-www-form-urlencoded`
- `multipart/form-data`

#### cookie

```python
cookie(name: str) -> Optional[str]
```

Get cookie value by name.

**Parameters:**
- `name` (str): Cookie name

**Returns:** Cookie value or None

#### set_state

```python
set_state(key: str, value: Any) -> None
```

Set a value in request state.

**Parameters:**
- `key` (str): State key
- `value` (Any): State value

---

## Response

Base HTTP response class.

### Constructor

```python
Response(
    content: Optional[bytes] = None,
    status_code: int = 200,
    headers: Optional[Headers] = None,
    media_type: Optional[str] = None
)
```

**Parameters:**
- `content` (bytes): Response body
- `status_code` (int): HTTP status code
- `headers` (Headers): Response headers
- `media_type` (str): Content-Type

**Example:**
```python
response = Response(
    b"Hello, World!",
    status_code=200,
    media_type="text/plain"
)
```

### Attributes

- `status_code` (int): HTTP status code
- `media_type` (Optional[str]): Content-Type
- `body` (bytes): Response body (read-only)
- `headers` (Headers): Response headers

### Methods

#### set_header

```python
set_header(key: str, value: str) -> None
```

Set a response header.

#### set_cookie

```python
set_cookie(
    key: str,
    value: str,
    max_age: Optional[int] = None,
    path: Optional[str] = None,
    domain: Optional[str] = None,
    secure: Optional[bool] = None,
    httponly: Optional[bool] = None,
    samesite: Optional[str] = None
) -> None
```

Set a cookie.

**Example:**
```python
response = JSONResponse({"logged_in": True})
response.set_cookie(
    "session_id",
    "abc123",
    max_age=3600,
    httponly=True,
    secure=True,
    samesite="lax"
)
```

---

## JSONResponse

JSON response class.

### Constructor

```python
JSONResponse(
    content: Any,
    status_code: int = 200,
    headers: Optional[Headers] = None
)
```

**Parameters:**
- `content` (Any): Python object to serialize as JSON
- `status_code` (int): HTTP status code
- `headers` (Headers): Additional headers

**Example:**
```python
return JSONResponse({
    "id": 123,
    "name": "John",
    "active": True
})
```

Automatically sets `Content-Type: application/json`.

---

## HTMLResponse

HTML response class.

### Constructor

```python
HTMLResponse(
    content: str,
    status_code: int = 200,
    headers: Optional[Headers] = None
)
```

**Parameters:**
- `content` (str): HTML string
- `status_code` (int): HTTP status code
- `headers` (Headers): Additional headers

**Example:**
```python
return HTMLResponse("""
<!DOCTYPE html>
<html>
    <body>
        <h1>Hello, Tachyon!</h1>
    </body>
</html>
""")
```

Automatically sets `Content-Type: text/html; charset=utf-8`.

---

## Route

HTTP route definition.

### Constructor

```python
Route(
    path: str,
    endpoint: Callable,
    methods: List[str] = ["GET"],
    name: Optional[str] = None
)
```

**Parameters:**
- `path` (str): URL path pattern (supports parameters: `/users/{user_id}`)
- `endpoint` (Callable): Async function to handle requests
- `methods` (List[str]): HTTP methods
- `name` (str): Optional route name

**Example:**
```python
async def get_user(request: Request):
    return JSONResponse({"user": "data"})

route = Route(
    "/users/{user_id}",
    get_user,
    methods=["GET"],
    name="get_user"
)
```

### Path Parameters

Tachyon supports path parameters using `{param_name}` syntax:

```python
Route("/users/{user_id}", handler)
Route("/posts/{post_id}/comments/{comment_id}", handler)
```

Access in handler:
```python
async def handler(request: Request):
    user_id = request.path_params.get("user_id")
    # ...
```

---

## WebSocketRoute

WebSocket route definition.

### Constructor

```python
WebSocketRoute(
    path: str,
    endpoint: Callable,
    name: Optional[str] = None
)
```

**Parameters:**
- `path` (str): WebSocket URL path
- `endpoint` (Callable): Async function to handle WebSocket
- `name` (str): Optional route name

**Example:**
```python
async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_json()
    await websocket.send_json({"echo": data})
    await websocket.close()

route = WebSocketRoute("/ws", websocket_handler)
```

---

## WebSocket

WebSocket connection object.

### Attributes

- `path` (str): WebSocket path
- `query_params` (QueryParams): Query parameters
- `path_params` (Dict[str, str]): Path parameters

### Methods

#### accept

```python
async accept() -> None
```

Accept the WebSocket connection.

**Must be called before sending/receiving messages.**

#### send_text

```python
async send_text(data: str) -> None
```

Send text message.

#### send_json

```python
async send_json(data: Any) -> None
```

Send JSON message (auto-serialized).

#### send_bytes

```python
async send_bytes(data: bytes) -> None
```

Send binary message.

#### receive_text

```python
async receive_text() -> str
```

Receive text message.

#### receive_json

```python
async receive_json() -> Any
```

Receive and parse JSON message.

#### receive_bytes

```python
async receive_bytes() -> bytes
```

Receive binary message.

#### close

```python
async close(code: int = 1000) -> None
```

Close the WebSocket connection.

**Parameters:**
- `code` (int): Close code (default: 1000 = normal closure)

**Example:**
```python
async def echo_ws(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_text(f"Echo: {message}")
    except Exception:
        pass
    finally:
        await websocket.close()
```

---

## Headers

Case-insensitive HTTP headers dictionary.

### Constructor

```python
Headers()
```

### Methods

#### get

```python
get(key: str) -> Optional[str]
```

Get header value (case-insensitive).

**Example:**
```python
content_type = headers.get("content-type")
# Same as:
content_type = headers.get("Content-Type")
```

#### set

```python
set(key: str, value: str) -> None
```

Set header value.

#### contains

```python
contains(key: str) -> bool
```

Check if header exists.

#### items

```python
items() -> Dict[str, str]
```

Get all headers as dictionary.

#### raw

```python
raw() -> List[Tuple[str, str]]
```

Get headers as list of tuples.

---

## QueryParams

URL query parameters.

### Methods

#### get

```python
get(key: str) -> Optional[str]
```

Get first value for a key.

**Example:**
```python
page = request.query_params.get("page")  # "1" from ?page=1
```

#### get_list

```python
get_list(key: str) -> List[str]
```

Get all values for a key (for multi-value params).

**Example:**
```python
tags = request.query_params.get_list("tags")
# ["python", "rust"] from ?tags=python&tags=rust
```

#### items

```python
items() -> Dict[str, Union[str, List[str]]]
```

Get all parameters as dictionary.

#### contains

```python
contains(key: str) -> bool
```

Check if parameter exists.

---

## UploadFile

Uploaded file object.

### Constructor

```python
UploadFile(
    filename: str,
    content_type: Optional[str] = None,
    content: bytes = b""
)
```

### Attributes

- `filename` (str): Original filename
- `content_type` (Optional[str]): MIME type
- `size` (Optional[int]): File size in bytes

### Methods

#### read

```python
read() -> bytes
```

Read entire file content.

#### read_bytes

```python
read_bytes(n: int) -> bytes
```

Read n bytes from file.

#### seek

```python
seek(position: int) -> None
```

Seek to position in file.

#### close

```python
close() -> None
```

Close the file.

#### save

```python
save(path: str) -> None
```

Save file to disk.

**Example:**
```python
async def upload_handler(request: Request):
    form = request.form()
    file = form.get("file")
    
    if isinstance(file, UploadFile):
        file.save(f"/uploads/{file.filename}")
        return JSONResponse({"saved": file.filename})
```

---

## TestClient

HTTP client for testing ASGI applications.

### Constructor

```python
TestClient(
    app: TachyonEngine,
    base_url: str = "http://testserver"
)
```

**Parameters:**
- `app` (TachyonEngine): Application to test
- `base_url` (str): Base URL for requests

### Methods

#### get

```python
get(
    url: str,
    params: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> TestResponse
```

Send GET request.

#### post

```python
post(
    url: str,
    json: Optional[Any] = None,
    data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> TestResponse
```

Send POST request.

#### put, delete, patch

Similar to `post`.

**Example:**
```python
app = TachyonEngine()

async def api_handler(request):
    return JSONResponse({"status": "ok"})

app.add_route(Route("/api/status", api_handler))

client = TestClient(app)
response = client.get("/api/status")
assert response.status_code == 200
```

### Context Manager

```python
with TestClient(app) as client:
    response = client.get("/")
    # ...
```

---

## TestResponse

Response from TestClient.

### Attributes

- `status_code` (int): HTTP status code
- `headers` (Dict[str, str]): Response headers

### Methods

#### content

```python
content() -> bytes
```

Get response body as bytes.

#### text

```python
text() -> str
```

Get response body as text.

#### json

```python
json() -> Any
```

Parse response body as JSON.

**Example:**
```python
response = client.post("/api/users", json={"name": "John"})
assert response.status_code == 201
data = response.json()
assert data["created"] == True
```

---

## Middleware

Middleware wrapper class.

### Constructor

```python
Middleware(cls: Type, **options)
```

**Parameters:**
- `cls`: Middleware class
- `**options`: Keyword arguments passed to middleware

**Example:**
```python
from tachyon_engine import Middleware

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        print(f"Request: {scope['method']} {scope['path']}")
        await self.app(scope, receive, send)

app.add_middleware(Middleware(LoggingMiddleware))
```

---

## Type Aliases

### Request Handler

```python
async def handler(request: Request) -> Response:
    # ...
    return JSONResponse({"data": "value"})
```

### WebSocket Handler

```python
async def ws_handler(websocket: WebSocket) -> None:
    await websocket.accept()
    # ...
    await websocket.close()
```

### Middleware Protocol

```python
class CustomMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Pre-processing
        await self.app(scope, receive, send)
        # Post-processing
```

---

## Error Handling

Tachyon Engine propagates Python exceptions normally:

```python
async def handler(request: Request):
    try:
        result = risky_operation()
        return JSONResponse({"result": result})
    except ValueError as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=400
        )
    except Exception as e:
        return JSONResponse(
            {"error": "Internal server error"},
            status_code=500
        )
```

---

## ASGI Protocol

Tachyon Engine fully implements ASGI 3.0:

```python
async def app(scope, receive, send):
    # Tachyon Engine handles this internally
    pass
```

Scope types:
- `http`: HTTP requests
- `websocket`: WebSocket connections
- `lifespan`: Application lifecycle events

---

## Performance Tips

### 1. Reuse Application Instance

```python
# ✅ Good - single instance
app = TachyonEngine()

# ❌ Bad - creating repeatedly
def get_app():
    return TachyonEngine()
```

### 2. Use Appropriate Response Types

```python
# ✅ Fast - JSONResponse
return JSONResponse({"data": value})

# ❌ Slower - Manual JSON encoding
import json
return Response(json.dumps({"data": value}).encode())
```

### 3. Access Headers Directly

```python
# ✅ Fast
auth = request.headers.get("authorization")

# ❌ Slower
headers_dict = dict(request.headers.items())
auth = headers_dict.get("authorization")
```

---

## Examples

### Basic API

```python
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

app = TachyonEngine()

async def list_users(request: Request):
    return JSONResponse({"users": []})

async def create_user(request: Request):
    data = request.json()
    return JSONResponse({"created": data}, status_code=201)

app.add_route(Route("/users", list_users, methods=["GET"]))
app.add_route(Route("/users", create_user, methods=["POST"]))
```

### With Path Parameters

```python
async def get_user(request: Request):
    user_id = request.path_params.get("user_id")
    return JSONResponse({
        "id": user_id,
        "name": f"User {user_id}"
    })

app.add_route(Route("/users/{user_id}", get_user))
```

### With Middleware

```python
class TimingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        import time
        start = time.time()
        await self.app(scope, receive, send)
        duration = time.time() - start
        print(f"Request took {duration:.3f}s")

app.add_middleware(Middleware(TimingMiddleware))
```

---

Next: Check out [Examples](examples.md) for more real-world usage

