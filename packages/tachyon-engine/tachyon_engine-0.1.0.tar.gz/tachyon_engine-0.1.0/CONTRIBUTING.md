# Contributing to Tachyon Engine

Thank you for your interest in contributing to Tachyon Engine! This document provides guidelines for contributions.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/tachyon-engine/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, Rust version)
   - Code samples if applicable

### Suggesting Features

1. Check [Discussions](https://github.com/yourusername/tachyon-engine/discussions) for similar ideas
2. Create a new discussion or issue explaining:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative solutions considered
   - How it benefits the project

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`: `git checkout -b feature/my-feature`
3. **Make your changes**:
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation
4. **Test** your changes:
   ```bash
   # Rust tests
   cargo test
   
   # Python tests
   pytest tests/
   
   # Linting
   cargo clippy
   cargo fmt --check
   ```
5. **Commit** with clear messages:
   ```
   feat: add support for custom middleware
   
   - Implement MiddlewareBuilder trait
   - Add tests for middleware stacking
   - Update documentation
   ```
6. **Push** to your fork: `git push origin feature/my-feature`
7. **Open a Pull Request** with:
   - Clear description of changes
   - Link to related issues
   - Screenshots/examples if applicable

## Development Setup

### Prerequisites

- **Rust 1.70+**: [Install Rust](https://rustup.rs/)
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **maturin**: `pip install maturin`

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/tachyon-engine.git
cd tachyon-engine

# Install development dependencies
pip install -r requirements-dev.txt

# Build in development mode
maturin develop

# Run tests
make test
```

## Code Style

### Rust

- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- Use `cargo fmt` for formatting
- Use `cargo clippy` for linting
- Maximum line length: 100 characters
- Document public APIs with `///` doc comments

Example:
```rust
/// Parse query parameters from a query string.
///
/// # Arguments
///
/// * `query_string` - Raw query string bytes
///
/// # Returns
///
/// QueryParams instance with parsed parameters
pub fn from_query_string(query_string: &[u8]) -> Self {
    // Implementation
}
```

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use `black` for formatting: `black .`
- Use type hints where possible
- Maximum line length: 88 characters (black default)
- Document with docstrings

Example:
```python
async def get_user(request: Request) -> JSONResponse:
    """
    Get user by ID.
    
    Args:
        request: Request containing user_id in path params
        
    Returns:
        JSONResponse with user data or 404
    """
    user_id = request.path_params.get("user_id")
    # Implementation
```

## Testing

### Rust Tests

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_router

# Run with output
cargo test -- --nocapture
```

Write tests for all new functionality:
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_feature() {
        // Arrange
        let input = create_input();
        
        // Act
        let result = function_under_test(input);
        
        // Assert
        assert_eq!(result, expected);
    }
}
```

### Python Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_routing.py

# With coverage
pytest --cov=tachyon_engine tests/
```

Write tests using pytest:
```python
def test_feature():
    # Arrange
    app = TachyonEngine()
    
    # Act
    result = app.some_method()
    
    # Assert
    assert result == expected
```

## Documentation

### Rust Documentation

```bash
# Generate and open docs
cargo doc --open
```

Document all public APIs:
```rust
/// Brief description.
///
/// More detailed explanation if needed.
///
/// # Examples
///
/// ```
/// use tachyon_engine::Request;
/// let request = Request::new();
/// ```
///
/// # Errors
///
/// Returns `Err` if...
pub fn function() -> Result<()> {
    // Implementation
}
```

### Python Documentation

Update relevant markdown files in `docs/`:
- `docs/getting-started.md` - For new features
- `docs/api-reference.md` - For API changes
- `docs/examples.md` - For usage examples

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(routing): add support for regex patterns in routes

- Implement regex matcher
- Add tests
- Update documentation

Closes #123
```

```
fix(request): handle empty query string correctly

Previously, empty query strings caused a panic.
Now returns empty QueryParams.

Fixes #456
```

## Performance

When adding features, consider performance:

1. **Benchmark** new code:
   ```bash
   cargo bench
   ```

2. **Profile** if needed:
   ```bash
   cargo build --release
   perf record --call-graph dwarf target/release/benchmark
   perf report
   ```

3. **Compare** before and after:
   - Run benchmarks on main branch
   - Run benchmarks on your branch
   - Document any significant changes

## Release Process

(For maintainers)

1. Update version in `Cargo.toml` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions will build and release

## Questions?

- **Discussions**: Ask in [GitHub Discussions](https://github.com/yourusername/tachyon-engine/discussions)
- **Discord**: Join our community (coming soon)
- **Email**: maintainers@tachyon-engine.dev (coming soon)

## Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Given credit in documentation

Thank you for contributing to Tachyon Engine! 🚀

