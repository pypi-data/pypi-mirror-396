use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

use crate::asgi::{AsgiReceive, AsgiScope, AsgiSend, ScopeType};
use crate::error::{Result, TachyonError};
use crate::middleware::{Middleware, stack::MiddlewareStack};
use crate::request::Request;
use crate::response::Response;
use crate::routing::{Route, Router, WebSocketRoute};
use crate::websocket::WebSocket;

/// TachyonEngine - Main ASGI application
#[pyclass]
pub struct TachyonEngine {
    router: Arc<RwLock<Router>>,
    middleware_stack: Arc<RwLock<MiddlewareStack>>,
    
    #[pyo3(get)]
    pub routes: Vec<Route>,
    
    #[pyo3(get)]
    pub state: PyObject,
    
    #[pyo3(get)]
    pub debug: bool,
    
    lifespan: Option<PyObject>,
}

#[pymethods]
impl TachyonEngine {
    #[new]
    #[pyo3(signature = (debug=false, lifespan=None))]
    pub fn new(py: Python, debug: bool, lifespan: Option<PyObject>) -> PyResult<Self> {
        let state = PyDict::new(py).into();
        
        Ok(Self {
            router: Arc::new(RwLock::new(Router::new())),
            middleware_stack: Arc::new(RwLock::new(MiddlewareStack::new())),
            routes: Vec::new(),
            state,
            debug,
            lifespan,
        })
    }
    
    /// ASGI __call__ method
    pub fn __call__<'py>(
        &self,
        py: Python<'py>,
        _scope: PyObject,
        _receive: PyObject,
        _send: PyObject,
    ) -> PyResult<&'py pyo3::types::PyAny> {
        // For now, return a simple coroutine
        // Full ASGI handling will be implemented with proper async runtime
        let code = r#"
async def asgi_handler():
    pass
result = asgi_handler()
"#;
        let module = pyo3::types::PyModule::from_code(py, code, "", "")?;
        module.getattr("result")
    }
    
    /// Add a route
    pub fn add_route(&mut self, route: Route) -> PyResult<()> {
        let mut router = self.router.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Router lock poisoned"))?;
        
        router.add_route(route.clone())
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        
        self.routes.push(route);
        
        Ok(())
    }
    
    /// Route decorator
    pub fn route(
        &mut self,
        _path: String,
        _methods: Option<Vec<String>>,
        _name: Option<String>,
    ) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            // Return a decorator function
            let decorator = pyo3::types::PyModule::from_code(
                py,
                r#"
def decorator(func):
    return func
"#,
                "",
                "",
            )?;
            
            Ok(decorator.getattr("decorator")?.into())
        })
    }
    
    /// Add middleware
    pub fn add_middleware(&mut self, middleware: Middleware) -> PyResult<()> {
        let mut stack = self.middleware_stack.write()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Middleware stack lock poisoned"))?;
        
        stack.add(middleware);
        
        Ok(())
    }
    
    /// Build middleware stack
    pub fn build_middleware_stack(&self, py: Python, app: PyObject) -> PyResult<PyObject> {
        let stack = self.middleware_stack.read()
            .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Middleware stack lock poisoned"))?;
        
        stack.build(py, app)
    }
    
    /// Run the server
    pub fn run(&self, _py: Python, host: Option<&str>, port: Option<u16>) -> PyResult<()> {
        let host = host.unwrap_or("127.0.0.1");
        let port = port.unwrap_or(8000);
        println!("Starting Tachyon Engine on {}:{}", host, port);
        println!("Press Ctrl+C to stop");
        
        // TODO: Start the actual HTTP server
        Ok(())
    }
    
    fn __repr__(&self) -> String {
        format!("TachyonEngine(routes={})", self.routes.len())
    }
}

impl TachyonEngine {
    /// Handle HTTP request (stub for now)
    async fn handle_http(
        _py: Python<'_>,
        _router: &Arc<RwLock<Router>>,
        _scope: AsgiScope,
        _receive: AsgiReceive,
        _send: AsgiSend,
    ) -> Result<()> {
        // TODO: Implement full HTTP handling
        Ok(())
    }
    
    /// Handle WebSocket connection (stub for now)
    async fn handle_websocket(
        _py: Python<'_>,
        _router: &Arc<RwLock<Router>>,
        _scope: AsgiScope,
        _receive: AsgiReceive,
        _send: AsgiSend,
    ) -> Result<()> {
        // TODO: Implement WebSocket handling
        Ok(())
    }
    
    /// Handle lifespan events (stub for now)
    async fn handle_lifespan(
        _py: Python<'_>,
        _receive: AsgiReceive,
        _send: AsgiSend,
    ) -> Result<()> {
        // TODO: Implement lifespan handling
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_tachyon_engine_creation() {
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let engine = TachyonEngine::new(py, false, None).unwrap();
            assert_eq!(engine.routes.len(), 0);
        });
    }
}

