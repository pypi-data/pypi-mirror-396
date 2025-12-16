# Getting Started with Tachyon Engine

This guide will help you install and create your first application with Tachyon Engine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Rust 1.70+** (only for building from source) - [Install Rust](https://rustup.rs/)

## Installation

### From PyPI (Recommended)

```bash
pip install tachyon-engine
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/tachyon-engine.git
cd tachyon-engine

# Build and install
pip install maturin
maturin develop --release
```

### Verify Installation

```python
import tachyon_engine
print(tachyon_engine.__version__)
```

## Your First Application

### Hello World

Create a file called `app.py`:

```python
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

# Create the application
app = TachyonEngine(debug=True)

# Define a handler
async def homepage(request: Request):
    return JSONResponse({
        "message": "Hello, Tachyon!",
        "version": "0.1.0"
    })

# Add the route
app.add_route(Route("/", homepage, methods=["GET"]))

if __name__ == "__main__":
    print("🚀 Tachyon Engine running!")
    print("Routes:")
    for route in app.routes:
        print(f"  {route.methods} {route.path}")
```

### Run the Application

```bash
python app.py
```

## Path Parameters

Extract variables from the URL path:

```python
async def get_user(request: Request):
    user_id = request.path_params.get("user_id")
    return JSONResponse({
        "user_id": user_id,
        "name": f"User {user_id}"
    })

app.add_route(Route("/users/{user_id}", get_user, methods=["GET"]))
```

## Query Parameters

Access query string parameters:

```python
async def search(request: Request):
    query = request.query_params.get("q")
    limit = request.query_params.get("limit") or "10"
    
    return JSONResponse({
        "query": query,
        "limit": int(limit),
        "results": []
    })

app.add_route(Route("/search", search, methods=["GET"]))
```

## Request Body

Handle JSON request bodies:

```python
async def create_user(request: Request):
    try:
        data = request.json()
        # Validate and process data
        return JSONResponse({
            "success": True,
            "user": data
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=400)

app.add_route(Route("/users", create_user, methods=["POST"]))
```

## Multiple HTTP Methods

Handle multiple methods on the same path:

```python
async def users_endpoint(request: Request):
    if request.method == "GET":
        return JSONResponse({"users": []})
    
    elif request.method == "POST":
        data = request.json()
        return JSONResponse({"created": data}, status_code=201)
    
    elif request.method == "DELETE":
        return JSONResponse({"deleted": True}, status_code=204)

app.add_route(
    Route("/users", users_endpoint, methods=["GET", "POST", "DELETE"])
)
```

## Response Types

### JSON Response

```python
from tachyon_engine import JSONResponse

response = JSONResponse({
    "key": "value",
    "number": 42
})
```

### HTML Response

```python
from tachyon_engine import HTMLResponse

response = HTMLResponse("""
<html>
    <body>
        <h1>Hello from Tachyon!</h1>
    </body>
</html>
""")
```

### Plain Text Response

```python
from tachyon_engine import Response

response = Response(
    b"Plain text content",
    media_type="text/plain"
)
```

## Headers and Cookies

### Reading Headers

```python
async def protected_route(request: Request):
    auth = request.headers.get("authorization")
    if not auth:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    return JSONResponse({"authenticated": True})
```

### Setting Headers

```python
response = JSONResponse({"data": "value"})
response.set_header("X-Custom-Header", "custom-value")
```

### Setting Cookies

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

## Error Handling

```python
async def safe_endpoint(request: Request):
    try:
        # Your logic here
        result = do_something()
        return JSONResponse({"result": result})
    
    except ValueError as e:
        return JSONResponse({
            "error": "Validation error",
            "detail": str(e)
        }, status_code=400)
    
    except Exception as e:
        return JSONResponse({
            "error": "Internal server error"
        }, status_code=500)
```

## Application State

Share data across requests:

```python
app = TachyonEngine()
app.state = {"counter": 0}

async def increment(request: Request):
    app.state["counter"] += 1
    return JSONResponse({
        "counter": app.state["counter"]
    })
```

## Next Steps

- Learn about [Best Practices](best-practices.md)
- Explore the [API Reference](api-reference.md)
- Check out [Examples](examples.md)
- Read about [Performance](performance.md)

## Common Issues

### Import Error

```python
ImportError: cannot import name 'TachyonEngine'
```

**Solution**: Make sure you've installed tachyon-engine:
```bash
pip install tachyon-engine
```

Or if building from source:
```bash
maturin develop
```

### Module Not Found

```python
ModuleNotFoundError: No module named 'tachyon_engine'
```

**Solution**: Ensure you're in the correct Python environment where tachyon-engine is installed.

## Getting Help

- **Documentation**: [Full docs](index.md)
- **GitHub Issues**: Report bugs or request features
- **Examples**: Check the `examples/` directory

---

Ready to learn more? Check out the [Best Practices](best-practices.md) guide!

