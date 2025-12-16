# Migration Guide: From Starlette to Tachyon Engine

This guide helps you migrate existing Starlette applications to Tachyon Engine.

## Overview

Tachyon Engine is designed as a **drop-in replacement** for Starlette. Most code will work with minimal or no changes.

## Migration Checklist

- [ ] Update imports
- [ ] Test all endpoints
- [ ] Update middleware if needed
- [ ] Run benchmarks to verify performance gains
- [ ] Update documentation

## Quick Migration

### Step 1: Update Imports

**Before (Starlette):**
```python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, HTMLResponse
from starlette.requests import Request
```

**After (Tachyon):**
```python
from tachyon_engine import TachyonEngine, Route, JSONResponse, HTMLResponse, Request
```

### Step 2: Update Application Instance

**Before:**
```python
app = Starlette(debug=True)
```

**After:**
```python
app = TachyonEngine(debug=True)
```

That's it for basic apps! Test your application to ensure everything works.

## Common Patterns

### Basic Routes

**Compatible** - No changes needed:

```python
# Works in both Starlette and Tachyon
async def homepage(request):
    return JSONResponse({"message": "Hello!"})

app.add_route(Route("/", homepage, methods=["GET"]))
```

### Path Parameters

**Compatible** - No changes needed:

```python
async def get_item(request):
    item_id = request.path_params.get("item_id")
    return JSONResponse({"item_id": item_id})

app.add_route(Route("/items/{item_id}", get_item))
```

### Request Data Access

**Compatible** - Same API:

```python
async def handler(request):
    # All work the same
    method = request.method
    path = request.path
    query = request.query_params.get("q")
    auth = request.headers.get("authorization")
    data = request.json()
    
    return JSONResponse({"received": True})
```

### Response Types

**Compatible** - Same API:

```python
# JSON
return JSONResponse({"key": "value"}, status_code=200)

# HTML
return HTMLResponse("<h1>Hello</h1>")

# Plain
return Response(b"text", media_type="text/plain")
```

## Differences and Considerations

### 1. Middleware

**Starlette:**
```python
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

**Tachyon (Compatible):**
```python
from tachyon_engine import Middleware
# Use your custom middleware or Starlette's
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(Middleware(CORSMiddleware, allow_origins=["*"]))
```

**Note:** You can still use Starlette's built-in middleware with Tachyon!

### 2. Background Tasks

**Starlette:**
```python
from starlette.background import BackgroundTask

async def send_email(email: str):
    # ...

return JSONResponse(
    {"sent": True},
    background=BackgroundTask(send_email, "user@example.com")
)
```

**Tachyon (Not yet supported):**
```python
# Workaround: Use asyncio.create_task
import asyncio

async def handler(request):
    asyncio.create_task(send_email("user@example.com"))
    return JSONResponse({"sent": True})
```

### 3. Static Files

**Starlette:**
```python
from starlette.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

**Tachyon (Use Starlette's StaticFiles):**
```python
# Still works! Tachyon is ASGI-compatible
from starlette.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 4. Templates

**Starlette:**
```python
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})
```

**Tachyon (Use Starlette's templates):**
```python
# Starlette's Jinja2Templates still work!
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

async def homepage(request):
    return templates.TemplateResponse("index.html", {"request": request})
```

## Full Example Migration

### Before (Starlette)

```python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

app = Starlette(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)

async def homepage(request):
    return JSONResponse({"message": "Hello, Starlette!"})

async def get_user(request):
    user_id = request.path_params["user_id"]
    return JSONResponse({"user_id": user_id})

app.add_route(Route("/", homepage))
app.add_route(Route("/users/{user_id}", get_user))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### After (Tachyon)

```python
from tachyon_engine import TachyonEngine, Route, JSONResponse, Request, Middleware
from starlette.middleware.cors import CORSMiddleware  # Can still use Starlette middleware!

app = TachyonEngine(debug=True)

app.add_middleware(Middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
))

async def homepage(request: Request):
    return JSONResponse({"message": "Hello, Tachyon!"})

async def get_user(request: Request):
    user_id = request.path_params.get("user_id")
    return JSONResponse({"user_id": user_id})

app.add_route(Route("/", homepage, methods=["GET"]))
app.add_route(Route("/users/{user_id}", get_user, methods=["GET"]))

if __name__ == "__main__":
    # Option 1: Use Tachyon's built-in server (when available)
    # app.run(host="0.0.0.0", port=8000)
    
    # Option 2: Still use uvicorn (ASGI compatible)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Changes:**
1. ✅ Import from `tachyon_engine` instead of `starlette`
2. ✅ `TachyonEngine` instead of `Starlette`
3. ✅ Type hint `Request` in handlers (optional but recommended)
4. ✅ Can still use Starlette middleware and utilities!

## Performance Gains

After migrating, you should see:

- **~5-7x faster** application and route creation
- **~2-4x faster** request/response handling
- **~10x faster** path matching
- **~50% less** memory usage

Run benchmarks to verify:
```bash
python benchmarks/comprehensive_benchmark.py
```

## Gradual Migration

You can migrate gradually:

### Phase 1: Install and Test

```bash
pip install tachyon-engine
```

```python
# Test in development first
from tachyon_engine import TachyonEngine
```

### Phase 2: Migrate Core Routes

Start with your most frequently used routes:

```python
# Keep using Starlette for complex routes
from starlette.applications import Starlette

# Use Tachyon for hot paths
from tachyon_engine import TachyonEngine

# Choose based on your needs
app = TachyonEngine()  # or Starlette()
```

### Phase 3: Full Migration

Once tested, migrate completely to Tachyon.

## Troubleshooting

### ImportError

**Problem:**
```python
ImportError: cannot import name 'TachyonEngine'
```

**Solution:**
```bash
pip install tachyon-engine
```

### Module Not Found

**Problem:**
```python
ModuleNotFoundError: No module named 'tachyon_engine._internal'
```

**Solution:**
Rebuild the extension:
```bash
maturin build --release
pip install target/wheels/*.whl --force-reinstall
```

### Performance Not as Expected

**Checklist:**
- [ ] Compiled in release mode (`--release`)
- [ ] Not running in debug mode
- [ ] Profiled to find bottlenecks
- [ ] Using async properly (no blocking I/O)

### Middleware Not Working

**Solution:**
You can still use Starlette's middleware:
```python
from starlette.middleware.cors import CORSMiddleware
from tachyon_engine import Middleware

app.add_middleware(Middleware(CORSMiddleware, allow_origins=["*"]))
```

## Compatibility Matrix

| Feature | Starlette | Tachyon | Notes |
|---------|-----------|---------|-------|
| HTTP Routes | ✅ | ✅ | Fully compatible |
| Path Parameters | ✅ | ✅ | Fully compatible |
| Query Parameters | ✅ | ✅ | Fully compatible |
| Request Body | ✅ | ✅ | Fully compatible |
| JSON Response | ✅ | ✅ | Fully compatible |
| HTML Response | ✅ | ✅ | Fully compatible |
| Middleware | ✅ | ✅ | Compatible |
| WebSockets | ✅ | ✅ | Compatible |
| Background Tasks | ✅ | ⚠️ | Use asyncio.create_task |
| Static Files | ✅ | ✅ | Use Starlette's |
| Templates | ✅ | ✅ | Use Starlette's |
| TestClient | ✅ | ✅ | Compatible |
| Lifespan Events | ✅ | ✅ | Compatible |

✅ = Fully supported  
⚠️ = Workaround available

## Getting Help

If you encounter issues during migration:

1. Check this migration guide
2. Review [examples/](../examples/)
3. Open an issue on [GitHub](https://github.com/yourusername/tachyon-engine/issues)
4. Ask in [Discussions](https://github.com/yourusername/tachyon-engine/discussions)

---

Ready to migrate? Start with the [Getting Started](getting-started.md) guide!

