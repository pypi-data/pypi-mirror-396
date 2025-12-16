use pyo3::prelude::*;

/// WebSocketRoute - Represents a WebSocket route
#[pyclass]
#[derive(Clone)]
pub struct WebSocketRoute {
    #[pyo3(get, set)]
    pub path: String,
    
    #[pyo3(get, set)]
    pub endpoint: PyObject,
    
    #[pyo3(get, set)]
    pub name: Option<String>,
}

#[pymethods]
impl WebSocketRoute {
    #[new]
    #[pyo3(signature = (path, endpoint, name=None))]
    pub fn new(
        path: String,
        endpoint: PyObject,
        name: Option<String>,
    ) -> Self {
        Self {
            path,
            endpoint,
            name,
        }
    }
    
    fn __repr__(&self) -> String {
        format!(
            "WebSocketRoute(path='{}', name={:?})",
            self.path, self.name
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_websocket_route_creation() {
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let handler = py.None();
            let route = WebSocketRoute::new(
                "/ws".to_string(),
                handler,
                Some("ws_route".to_string()),
            );
            
            assert_eq!(route.path, "/ws");
            assert_eq!(route.name, Some("ws_route".to_string()));
        });
    }
}

