# Tachyon Engine - Guía de Inicio Rápido

## 🚀 Instalación

### Pre-requisitos

- Rust 1.70+ (https://rustup.rs/)
- Python 3.8+
- pip

### Compilar desde Fuente

```bash
# Clonar el repositorio (si aplica)
cd tachyon-engine

# Opción 1: Compilar wheel
pip install maturin
maturin build --release

# El wheel estará en: target/wheels/tachyon_engine-0.1.0-*.whl
pip install target/wheels/tachyon_engine-0.1.0-*.whl

# Opción 2: Desarrollo (con virtualenv)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install maturin
maturin develop
```

## 📝 Uso Básico

### Ejemplo Mínimo

```python
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

# Crear aplicación
app = TachyonEngine(debug=True)

# Definir handler
async def homepage(request: Request):
    return JSONResponse({
        "message": "Hello from Tachyon Engine!",
        "path": request.path,
    })

# Agregar ruta
app.add_route(Route("/", homepage, methods=["GET"]))

# Ver rutas registradas
print(f"Routes: {len(app.routes)}")
for route in app.routes:
    print(f"  {route.methods} {route.path}")
```

### Ejemplo con Path Parameters

```python
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

app = TachyonEngine()

async def user_detail(request: Request):
    user_id = request.path_params.get("user_id")
    return JSONResponse({
        "user_id": user_id,
        "message": f"User {user_id} details",
    })

app.add_route(Route("/users/{user_id}", user_detail, methods=["GET"]))
```

### Ejemplo con JSON Body

```python
async def create_user(request: Request):
    try:
        data = request.json()
        # Procesar data
        return JSONResponse({
            "success": True,
            "created": data,
        }, status_code=201)
    except Exception as e:
        return JSONResponse({
            "error": str(e),
        }, status_code=400)

app.add_route(Route("/users", create_user, methods=["POST"]))
```

### Ejemplo con Query Parameters

```python
async def search_users(request: Request):
    query = request.query_params.get("q")
    limit = request.query_params.get("limit") or "10"
    
    return JSONResponse({
        "query": query,
        "limit": int(limit),
        "results": [],
    })

app.add_route(Route("/search", search_users, methods=["GET"]))
```

### Ejemplo con Headers y Cookies

```python
async def protected_route(request: Request):
    auth_header = request.headers.get("authorization")
    session_id = request.cookie("session_id")
    
    if not auth_header:
        return JSONResponse({
            "error": "Unauthorized",
        }, status_code=401)
    
    response = JSONResponse({
        "authenticated": True,
        "session": session_id,
    })
    
    # Set cookie
    response.set_cookie(
        "last_visit",
        "2024-01-01",
        max_age=3600,
        httponly=True,
    )
    
    return response

app.add_route(Route("/protected", protected_route, methods=["GET"]))
```

## 🧪 Testing

### Usar TestClient

```python
from tachyon_engine import TachyonEngine, Route, TestClient, JSONResponse

app = TachyonEngine()

@app.route("/test")
async def test_endpoint(request):
    return JSONResponse({"status": "ok"})

app.add_route(Route("/test", test_endpoint, methods=["GET"]))

# Test
client = TestClient(app)
response = client.get("/test")
assert response.status_code == 200
# assert response.json() == {"status": "ok"}  # Requiere implementación completa
```

### Tests con Pytest

```python
import pytest
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

def test_basic_route():
    app = TachyonEngine()
    
    async def handler(request: Request):
        return JSONResponse({"test": True})
    
    app.add_route(Route("/test", handler, methods=["GET"]))
    
    assert len(app.routes) == 1
    assert app.routes[0].path == "/test"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## ⚡ Benchmarks

### Ejecutar Benchmarks

```bash
# Benchmarks Rust (routing performance)
cargo bench

# Benchmarks vs Starlette
python benchmarks/benchmark_vs_starlette.py
```

## 📚 API Reference

### TachyonEngine

```python
class TachyonEngine:
    def __init__(self, debug: bool = False, lifespan = None):
        """Crear aplicación ASGI"""
        
    def add_route(self, route: Route) -> None:
        """Agregar ruta"""
        
    async def __call__(self, scope, receive, send):
        """ASGI application callable"""
        
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Iniciar servidor (próximamente)"""
```

### Request

```python
class Request:
    method: str
    url: str
    path: str
    headers: Headers
    query_params: QueryParams
    path_params: Dict[str, str]
    cookies: Dict[str, str]
    state: Dict[str, Any]
    
    def body() -> bytes:
        """Leer body completo"""
        
    def json() -> Any:
        """Parse JSON body"""
        
    def form() -> Dict:
        """Parse form data"""
        
    def cookie(name: str) -> Optional[str]:
        """Obtener cookie por nombre"""
```

### Response

```python
class Response:
    status_code: int
    media_type: Optional[str]
    
    def set_header(key: str, value: str):
        """Set header"""
        
    def set_cookie(
        key: str,
        value: str,
        max_age: Optional[int] = None,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        secure: Optional[bool] = None,
        httponly: Optional[bool] = None,
        samesite: Optional[str] = None,
    ):
        """Set cookie"""

class JSONResponse(Response):
    """Auto-serializa a JSON"""

class HTMLResponse(Response):
    """Response HTML"""
```

### Route

```python
class Route:
    def __init__(
        self,
        path: str,
        endpoint: Callable,
        methods: List[str] = ["GET"],
        name: Optional[str] = None,
    ):
        """Definir ruta HTTP"""
```

## 🔧 Comandos Make

```bash
make build        # Compilar release
make develop      # Compilar e instalar en desarrollo
make test         # Ejecutar todos los tests
make test-rust    # Solo tests Rust
make test-python  # Solo tests Python
make bench        # Ejecutar benchmarks
make clean        # Limpiar artifacts
```

## 📖 Ejemplos Completos

Ver `/examples/simple_app.py` para un ejemplo completo funcional.

## 🐛 Debugging

### Ver warnings de compilación

```bash
cargo build 2>&1 | grep "warning:"
```

### Ejecutar con logs

```python
import logging
logging.basicConfig(level=logging.DEBUG)

app = TachyonEngine(debug=True)
# ...
```

## 🤝 Contribuir

1. Fork el repo
2. Crea una feature branch
3. Implementa con tests
4. Ejecuta `cargo fmt` y `cargo clippy`
5. Submit PR

## 📄 Más Información

- `README.md`: Documentación completa
- `IMPLEMENTATION_NOTES.md`: Notas técnicas de implementación
- Documentación de Starlette: https://www.starlette.io/

---

**Versión**: 0.1.0  
**Status**: ✅ Compilando exitosamente  
**Próximo**: Implementación completa del servidor ASGI

