use pyo3::prelude::*;

/// Route - Represents a single HTTP route
#[pyclass]
#[derive(Clone)]
pub struct Route {
    #[pyo3(get, set)]
    pub path: String,
    
    #[pyo3(get, set)]
    pub endpoint: PyObject,
    
    #[pyo3(get, set)]
    pub methods: Vec<String>,
    
    #[pyo3(get, set)]
    pub name: Option<String>,
}

#[pymethods]
impl Route {
    #[new]
    #[pyo3(signature = (path, endpoint, methods=vec!["GET".to_string()], name=None))]
    pub fn new(
        path: String,
        endpoint: PyObject,
        methods: Vec<String>,
        name: Option<String>,
    ) -> Self {
        Self {
            path,
            endpoint,
            methods,
            name,
        }
    }
    
    fn __repr__(&self) -> String {
        format!(
            "Route(path='{}', methods={:?}, name={:?})",
            self.path, self.methods, self.name
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_route_creation() {
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let handler = py.None();
            let route = Route::new(
                "/test".to_string(),
                handler,
                vec!["GET".to_string(), "POST".to_string()],
                Some("test_route".to_string()),
            );
            
            assert_eq!(route.path, "/test");
            assert_eq!(route.methods, vec!["GET", "POST"]);
            assert_eq!(route.name, Some("test_route".to_string()));
        });
    }
}

