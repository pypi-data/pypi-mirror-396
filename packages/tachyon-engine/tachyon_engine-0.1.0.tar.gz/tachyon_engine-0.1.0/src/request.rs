use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;

use crate::asgi::{AsgiReceive, AsgiScope};
use crate::datastructures::{Headers, QueryParams};
use crate::error::{Result, TachyonError};

/// Request - HTTP Request object
#[pyclass]
pub struct Request {
    #[pyo3(get)]
    method: String,
    
    #[pyo3(get)]
    url: String,
    
    #[pyo3(get)]
    path: String,
    
    headers: Headers,
    query_params: QueryParams,
    path_params: HashMap<String, String>,
    
    scope: AsgiScope,
    receive: AsgiReceive,
    
    // Cached body
    body_cache: Option<Vec<u8>>,
    
    // Per-request state
    state: HashMap<String, PyObject>,
}

#[pymethods]
impl Request {
    /// Get headers
    #[getter]
    pub fn headers(&self) -> Headers {
        self.headers.clone()
    }
    
    /// Get query parameters
    #[getter]
    pub fn query_params(&self) -> QueryParams {
        self.query_params.clone()
    }
    
    /// Get path parameters
    #[getter]
    pub fn path_params(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        for (key, value) in &self.path_params {
            dict.set_item(key, value)?;
        }
        Ok(dict.into())
    }
    
    /// Get request state
    #[getter]
    pub fn state(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        for (key, value) in &self.state {
            dict.set_item(key, value)?;
        }
        Ok(dict.into())
    }
    
    /// Set state value
    pub fn set_state(&mut self, key: String, value: PyObject) {
        self.state.insert(key, value);
    }
    
    /// Read request body
    pub fn body<'py>(&mut self, py: Python<'py>) -> PyResult<&'py pyo3::types::PyBytes> {
        if self.body_cache.is_none() {
            // This needs to be async in real implementation
            // For now, return empty
            self.body_cache = Some(Vec::new());
        }
        
        Ok(pyo3::types::PyBytes::new(py, self.body_cache.as_ref().unwrap()))
    }
    
    /// Parse JSON body
    pub fn json(&mut self, py: Python) -> PyResult<PyObject> {
        let body = if let Some(ref cached) = self.body_cache {
            cached.clone()
        } else {
            Vec::new()
        };
        
        let json_value: serde_json::Value = serde_json::from_slice(&body)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        
        pythonize::pythonize(py, &json_value)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }
    
    /// Parse form data
    pub fn form(&mut self, py: Python) -> PyResult<PyObject> {
        let body = if let Some(ref cached) = self.body_cache {
            cached.clone()
        } else {
            Vec::new()
        };
        
        let content_type = self.headers.content_type()
            .unwrap_or_else(|| "application/x-www-form-urlencoded".to_string());
        
        if content_type.starts_with("application/x-www-form-urlencoded") {
            let params = QueryParams::from_query_string(&body);
            params.items(py)
        } else if content_type.starts_with("multipart/form-data") {
            // TODO: Implement multipart parsing
            Ok(PyDict::new(py).into())
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(
                "Unsupported content type for form parsing",
            ))
        }
    }
    
    /// Get cookie value
    pub fn cookie(&self, name: &str) -> Option<String> {
        let cookie_header = self.headers.get("cookie")?;
        
        for cookie in cookie_header.split(';') {
            let cookie = cookie.trim();
            if let Some(eq_pos) = cookie.find('=') {
                let (key, value) = cookie.split_at(eq_pos);
                if key == name {
                    return Some(value[1..].to_string());
                }
            }
        }
        
        None
    }
    
    /// Get all cookies
    #[getter]
    pub fn cookies(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        
        if let Some(cookie_header) = self.headers.get("cookie") {
            for cookie in cookie_header.split(';') {
                let cookie = cookie.trim();
                if let Some(eq_pos) = cookie.find('=') {
                    let (key, value) = cookie.split_at(eq_pos);
                    dict.set_item(key.trim(), value[1..].trim())?;
                }
            }
        }
        
        Ok(dict.into())
    }
    
    fn __repr__(&self) -> String {
        format!("Request(method='{}', url='{}')", self.method, self.url)
    }
}

impl Request {
    /// Create Request from ASGI scope and receive callable
    pub fn from_asgi(
        scope: AsgiScope,
        receive: AsgiReceive,
        path_params: HashMap<String, String>,
    ) -> Self {
        let headers = Headers::from_asgi_headers(&scope.headers);
        let query_params = QueryParams::from_query_string(&scope.query_string);
        
        let url = if scope.query_string.is_empty() {
            format!("{}://{}{}", scope.scheme, scope.server.as_ref().map(|(h, p)| format!("{}:{}", h, p)).unwrap_or_default(), scope.path)
        } else {
            format!(
                "{}://{}{}?{}",
                scope.scheme,
                scope.server.as_ref().map(|(h, p)| format!("{}:{}", h, p)).unwrap_or_default(),
                scope.path,
                String::from_utf8_lossy(&scope.query_string)
            )
        };
        
        Self {
            method: scope.method.clone(),
            url,
            path: scope.path.clone(),
            headers,
            query_params,
            path_params,
            scope,
            receive,
            body_cache: None,
            state: HashMap::new(),
        }
    }
    
    /// Load body asynchronously
    pub async fn load_body(&mut self, py: Python<'_>) -> PyResult<()> {
        if self.body_cache.is_none() {
            let body = self.receive.receive_body(py).await?;
            self.body_cache = Some(body);
        }
        Ok(())
    }
}

// Add pythonize dependency for JSON conversion
pub(crate) mod pythonize {
    use pyo3::prelude::*;
    use pyo3::types::{PyDict, PyList};
    use serde_json::Value;
    
    pub fn pythonize(py: Python, value: &Value) -> PyResult<PyObject> {
        match value {
            Value::Null => Ok(py.None()),
            Value::Bool(b) => Ok(b.into_py(py)),
            Value::Number(n) => {
                if let Some(i) = n.as_i64() {
                    Ok(i.into_py(py))
                } else if let Some(f) = n.as_f64() {
                    Ok(f.into_py(py))
                } else {
                    Ok(py.None())
                }
            }
            Value::String(s) => Ok(s.into_py(py)),
            Value::Array(arr) => {
                let list = PyList::empty(py);
                for item in arr {
                    list.append(pythonize(py, item)?)?;
                }
                Ok(list.into())
            }
            Value::Object(obj) => {
                let dict = PyDict::new(py);
                for (key, value) in obj {
                    dict.set_item(key, pythonize(py, value)?)?;
                }
                Ok(dict.into())
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    // Tests will be added with integration tests
}

