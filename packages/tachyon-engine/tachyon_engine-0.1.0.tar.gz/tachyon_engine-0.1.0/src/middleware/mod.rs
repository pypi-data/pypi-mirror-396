pub mod stack;

use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Middleware wrapper for Python middleware classes
#[pyclass]
#[derive(Clone)]
pub struct Middleware {
    #[pyo3(get)]
    pub cls: PyObject,
    
    options: PyObject,
}

#[pymethods]
impl Middleware {
    #[new]
    #[pyo3(signature = (cls, **kwargs))]
    pub fn new(py: Python, cls: PyObject, kwargs: Option<&PyDict>) -> PyResult<Self> {
        let options = if let Some(kw) = kwargs {
            kw.into()
        } else {
            PyDict::new(py).into()
        };
        
        Ok(Self { cls, options })
    }
    
    /// Instantiate the middleware with an app
    pub fn instantiate(&self, py: Python, app: PyObject) -> PyResult<PyObject> {
        // Call middleware class with app and **options
        let args = pyo3::types::PyTuple::new(py, &[app]);
        
        if let Ok(dict) = self.options.downcast::<PyDict>(py) {
            self.cls.call(py, args, Some(dict))
        } else {
            self.cls.call1(py, args)
        }
    }
    
    fn __repr__(&self) -> String {
        format!("Middleware({:?})", self.cls)
    }
}

/// ASGI Middleware Protocol
/// 
/// Middlewares must implement:
/// ```python
/// class MyMiddleware:
///     def __init__(self, app):
///         self.app = app
///     
///     async def __call__(self, scope, receive, send):
///         # Pre-processing
///         await self.app(scope, receive, send)
///         # Post-processing
/// ```
pub trait AsgiMiddleware {
    fn call(
        &self,
        scope: PyObject,
        receive: PyObject,
        send: PyObject,
    ) -> PyResult<PyObject>;
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_middleware_creation() {
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let cls = py.None();
            let middleware = Middleware::new(py, cls, None).unwrap();
            
            assert!(middleware.cls.is_none(py));
        });
    }
}

