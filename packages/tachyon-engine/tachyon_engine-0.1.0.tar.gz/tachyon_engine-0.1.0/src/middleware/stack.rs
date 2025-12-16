use pyo3::prelude::*;

use super::Middleware;

/// MiddlewareStack - Manages middleware composition (LIFO)
pub struct MiddlewareStack {
    middlewares: Vec<Middleware>,
}

impl MiddlewareStack {
    pub fn new() -> Self {
        Self {
            middlewares: Vec::new(),
        }
    }
    
    /// Add middleware to the stack
    pub fn add(&mut self, middleware: Middleware) {
        self.middlewares.push(middleware);
    }
    
    /// Build middleware stack by wrapping app
    /// Middlewares are applied in LIFO order (last added wraps first)
    pub fn build(&self, py: Python, app: PyObject) -> PyResult<PyObject> {
        let mut wrapped_app = app;
        
        // Apply middlewares in reverse order (LIFO)
        for middleware in self.middlewares.iter().rev() {
            wrapped_app = middleware.instantiate(py, wrapped_app)?;
        }
        
        Ok(wrapped_app)
    }
    
    /// Get middleware count
    pub fn len(&self) -> usize {
        self.middlewares.len()
    }
    
    /// Check if stack is empty
    pub fn is_empty(&self) -> bool {
        self.middlewares.is_empty()
    }
}

impl Default for MiddlewareStack {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_middleware_stack() {
        let mut stack = MiddlewareStack::new();
        
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let middleware1 = Middleware::new(py, py.None(), None).unwrap();
            let middleware2 = Middleware::new(py, py.None(), None).unwrap();
            
            stack.add(middleware1);
            stack.add(middleware2);
            
            assert_eq!(stack.len(), 2);
        });
    }
}

