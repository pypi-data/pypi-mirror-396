# ⚡ Tachyon Engine

> High-performance, Rust-powered alternative to Starlette for Python web applications

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Rust](https://img.shields.io/badge/rust-1.70+-orange.svg)](https://rust-lang.org)

**Tachyon Engine** is a blazingly fast Python web framework built in Rust. It provides a **drop-in replacement** for Starlette with **4-7x better performance** while maintaining full API compatibility.

## 🚀 Key Features

- **⚡ 4.78x faster** than Starlette on average
- **🔄 Drop-in replacement** - minimal code changes needed
- **🦀 Rust-powered** - leveraging Tokio and Hyper for maximum performance
- **🐍 Python-friendly** - seamless PyO3 integration
- **🛡️ Memory safe** - no manual memory management
- **🔌 ASGI 3.0 compatible** - works with existing ASGI ecosystem
- **🧪 Well tested** - comprehensive test suite

## 📊 Performance

Real benchmark results comparing Tachyon Engine vs Starlette:

| Operation | Tachyon | Starlette | Speedup |
|-----------|---------|-----------|---------|
| **Application Creation** | 2.76M ops/s | 476K ops/s | **5.79x** 🚀 |
| **Route Creation** | 2.17M ops/s | 320K ops/s | **6.80x** 🚀 |
| **Adding 10 Routes** | 107K ops/s | 25K ops/s | **4.22x** ⚡ |
| **JSON Response** | 431K ops/s | 187K ops/s | **2.30x** ⚡ |

**Average: 4.78x faster than Starlette** ✨

Run your own benchmarks:
```bash
python benchmarks/comprehensive_benchmark.py
```

## 📦 Installation

```bash
pip install tachyon-engine
```

### From Source

```bash
# Install maturin
pip install maturin

# Build and install
maturin build --release
pip install target/wheels/*.whl
```

## 🎯 Quick Start

### Basic Application

```python
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

app = TachyonEngine()

async def homepage(request: Request):
    return JSONResponse({"message": "Hello, Tachyon!"})

app.add_route(Route("/", homepage, methods=["GET"]))
```

### Run with uvicorn

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Complete REST API Example

```python
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

app = TachyonEngine(debug=True)

# In-memory database
users = {}

async def list_users(request: Request):
    return JSONResponse({"users": list(users.values())})

async def get_user(request: Request):
    user_id = request.path_params.get("user_id")
    if user_id not in users:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return JSONResponse({"user": users[user_id]})

async def create_user(request: Request):
    data = request.json()
    user_id = str(len(users) + 1)
    users[user_id] = {"id": user_id, "name": data.get("name")}
    return JSONResponse(users[user_id], status_code=201)

# Register routes
app.add_route(Route("/users", list_users, methods=["GET"]))
app.add_route(Route("/users/{user_id}", get_user, methods=["GET"]))
app.add_route(Route("/users", create_user, methods=["POST"]))
```

## 🔄 Migrating from Starlette

Tachyon Engine is designed as a **drop-in replacement**. Most Starlette code works with minimal changes:

**Before (Starlette):**
```python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse

app = Starlette(debug=True)
```

**After (Tachyon):**
```python
from tachyon_engine import TachyonEngine, Route, JSONResponse

app = TachyonEngine(debug=True)
```

See the [Migration Guide](docs/migration.md) for detailed instructions.

## 📚 Documentation

- [Getting Started](docs/getting-started.md) - Installation and basic usage
- [API Reference](docs/api-reference.md) - Complete API documentation
- [Architecture](docs/architecture.md) - Design and internals
- [Performance](docs/performance.md) - Benchmarks and optimization
- [Best Practices](docs/best-practices.md) - Coding patterns and tips
- [Migration Guide](docs/migration.md) - From Starlette to Tachyon
- [Examples](docs/examples.md) - Real-world code examples

## 🛠️ Development

### Prerequisites

- Python 3.8+
- Rust 1.70+
- Maturin

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/tachyon-engine.git
cd tachyon-engine

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install maturin
pip install maturin

# Build in development mode
maturin develop

# Install dev dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Python tests
pytest tests/

# Rust tests
cargo test --workspace

# All tests
make test
```

### Benchmarks

```bash
# Compare with Starlette
python benchmarks/comprehensive_benchmark.py

# Rust-only benchmarks
cargo bench
```

### Linting

```bash
# Rust
cargo clippy --workspace -- -D warnings

# Python
flake8 tests/ benchmarks/
black tests/ benchmarks/ --check
```

## 🏗️ Architecture

Tachyon Engine consists of:

- **Rust Core** (`src/`) - High-performance implementation using:
  - **Tokio** - Async runtime
  - **Hyper** - HTTP server
  - **PyO3** - Python bindings
  - **Matchit** - Fast path routing
  - **Serde** - JSON serialization

- **Python Layer** (`python/`) - Pythonic API and type hints

- **ASGI Bridge** - Full ASGI 3.0 protocol support

See [Architecture](docs/architecture.md) for details.

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Starlette** - API design inspiration
- **Tokio** - Async runtime
- **PyO3** - Rust-Python interoperability
- **Hyper** - HTTP implementation

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/tachyon-engine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/tachyon-engine/discussions)

## 🗺️ Roadmap

- [x] Core ASGI 3.0 implementation
- [x] HTTP routing with path parameters
- [x] Request/Response objects
- [x] JSON serialization
- [x] WebSocket support
- [x] Middleware system
- [x] Test client
- [ ] Background tasks
- [ ] Static file serving
- [ ] Template support
- [ ] OpenAPI/Swagger integration
- [ ] GraphQL support
- [ ] HTTP/2 and HTTP/3
- [ ] Built-in caching layer

## ⭐ Star History

If you find Tachyon Engine useful, please star the repository!

## 🔖 Related Projects

- [Starlette](https://github.com/encode/starlette) - Original Python web framework
- [FastAPI](https://github.com/tiangolo/fastapi) - Modern API framework built on Starlette
- [Actix-web](https://github.com/actix/actix-web) - Rust web framework
- [PyO3](https://github.com/PyO3/pyo3) - Rust-Python bindings

---

Made with ⚡ and 🦀 by the Tachyon Engine team
