use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;

use crate::asgi::AsgiSend;
use crate::datastructures::Headers;

/// Base Response class
#[pyclass]
#[derive(Clone)]
pub struct Response {
    #[pyo3(get, set)]
    pub status_code: u16,
    
    content: Vec<u8>,
    headers: Headers,
    
    #[pyo3(get, set)]
    pub media_type: Option<String>,
}

#[pymethods]
impl Response {
    #[new]
    #[pyo3(signature = (content=None, status_code=200, headers=None, media_type=None))]
    pub fn new(
        content: Option<Vec<u8>>,
        status_code: Option<u16>,
        headers: Option<Headers>,
        media_type: Option<String>,
    ) -> Self {
        let mut resp_headers = headers.unwrap_or_default();
        
        let media = media_type.or_else(|| Some("text/plain".to_string()));
        if let Some(ref mt) = media {
            if !resp_headers.contains("content-type") {
                resp_headers.set("content-type".to_string(), mt.clone());
            }
        }
        
        Self {
            status_code: status_code.unwrap_or(200),
            content: content.unwrap_or_default(),
            headers: resp_headers,
            media_type: media,
        }
    }
    
    /// Get response body
    #[getter]
    pub fn body<'py>(&self, py: Python<'py>) -> &'py pyo3::types::PyBytes {
        pyo3::types::PyBytes::new(py, &self.content)
    }
    
    /// Set response body
    #[setter]
    pub fn set_body(&mut self, content: Vec<u8>) {
        self.content = content;
    }
    
    /// Get headers
    #[getter]
    pub fn headers(&self) -> Headers {
        self.headers.clone()
    }
    
    /// Set header
    pub fn set_header(&mut self, key: String, value: String) {
        self.headers.set(key, value);
    }
    
    /// Set cookie
    pub fn set_cookie(
        &mut self,
        key: String,
        value: String,
        max_age: Option<i64>,
        path: Option<String>,
        domain: Option<String>,
        secure: Option<bool>,
        httponly: Option<bool>,
        samesite: Option<String>,
    ) {
        let mut cookie = format!("{}={}", key, value);
        
        if let Some(age) = max_age {
            cookie.push_str(&format!("; Max-Age={}", age));
        }
        if let Some(p) = path {
            cookie.push_str(&format!("; Path={}", p));
        }
        if let Some(d) = domain {
            cookie.push_str(&format!("; Domain={}", d));
        }
        if secure.unwrap_or(false) {
            cookie.push_str("; Secure");
        }
        if httponly.unwrap_or(false) {
            cookie.push_str("; HttpOnly");
        }
        if let Some(ss) = samesite {
            cookie.push_str(&format!("; SameSite={}", ss));
        }
        
        self.headers.set("set-cookie".to_string(), cookie);
    }
    
    fn __repr__(&self) -> String {
        format!("Response(status_code={})", self.status_code)
    }
}

impl Response {
    /// Send response via ASGI
    pub async fn send(&self, py: Python<'_>, send: &AsgiSend) -> PyResult<()> {
        // Send response start
        let headers = self.headers.to_asgi_headers();
        send.send_response_start(py, self.status_code, headers).await?;
        
        // Send response body
        send.send_response_body(py, self.content.clone(), false).await?;
        
        Ok(())
    }
}

/// JSON Response class
#[pyclass]
#[derive(Clone)]
pub struct JSONResponse {
    #[pyo3(get, set)]
    pub status_code: u16,
    
    content: Vec<u8>,
    headers: Headers,
    
    #[pyo3(get, set)]
    pub media_type: Option<String>,
}

#[pymethods]
impl JSONResponse {
    #[new]
    #[pyo3(signature = (content, status_code=200, headers=None))]
    pub fn new(
        py: Python,
        content: PyObject,
        status_code: Option<u16>,
        headers: Option<Headers>,
    ) -> PyResult<Self> {
        // Convert Python object to JSON
        let json_value = depythonize::depythonize(py, content)?;
        let json_bytes = serde_json::to_vec(&json_value)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        
        let mut resp_headers = headers.unwrap_or_default();
        resp_headers.set("content-type".to_string(), "application/json".to_string());
        
        Ok(Self {
            status_code: status_code.unwrap_or(200),
            content: json_bytes,
            headers: resp_headers,
            media_type: Some("application/json".to_string()),
        })
    }
    
    /// Get response body
    #[getter]
    pub fn body<'py>(&self, py: Python<'py>) -> &'py pyo3::types::PyBytes {
        pyo3::types::PyBytes::new(py, &self.content)
    }
    
    /// Get headers
    #[getter]
    pub fn headers(&self) -> Headers {
        self.headers.clone()
    }
    
    fn __repr__(&self) -> String {
        format!("JSONResponse(status_code={})", self.status_code)
    }
}

impl JSONResponse {
    /// Send response via ASGI
    pub async fn send(&self, py: Python<'_>, send: &AsgiSend) -> PyResult<()> {
        let headers = self.headers.to_asgi_headers();
        send.send_response_start(py, self.status_code, headers).await?;
        send.send_response_body(py, self.content.clone(), false).await?;
        Ok(())
    }
}

/// HTML Response class
#[pyclass]
#[derive(Clone)]
pub struct HTMLResponse {
    #[pyo3(get, set)]
    pub status_code: u16,
    
    content: Vec<u8>,
    headers: Headers,
    
    #[pyo3(get, set)]
    pub media_type: Option<String>,
}

#[pymethods]
impl HTMLResponse {
    #[new]
    #[pyo3(signature = (content, status_code=200, headers=None))]
    pub fn new(
        content: String,
        status_code: Option<u16>,
        headers: Option<Headers>,
    ) -> Self {
        let mut resp_headers = headers.unwrap_or_default();
        resp_headers.set("content-type".to_string(), "text/html; charset=utf-8".to_string());
        
        Self {
            status_code: status_code.unwrap_or(200),
            content: content.into_bytes(),
            headers: resp_headers,
            media_type: Some("text/html".to_string()),
        }
    }
    
    /// Get response body
    #[getter]
    pub fn body<'py>(&self, py: Python<'py>) -> &'py pyo3::types::PyBytes {
        pyo3::types::PyBytes::new(py, &self.content)
    }
    
    /// Get headers
    #[getter]
    pub fn headers(&self) -> Headers {
        self.headers.clone()
    }
    
    fn __repr__(&self) -> String {
        format!("HTMLResponse(status_code={})", self.status_code)
    }
}

impl HTMLResponse {
    /// Send response via ASGI
    pub async fn send(&self, py: Python<'_>, send: &AsgiSend) -> PyResult<()> {
        let headers = self.headers.to_asgi_headers();
        send.send_response_start(py, self.status_code, headers).await?;
        send.send_response_body(py, self.content.clone(), false).await?;
        Ok(())
    }
}

// Helper module to convert Python objects to JSON
mod depythonize {
    use pyo3::prelude::*;
    use pyo3::types::{PyBool, PyDict, PyFloat, PyInt, PyList, PyString};
    use serde_json::Value;
    
    pub fn depythonize(py: Python, obj: PyObject) -> PyResult<Value> {
        let any = obj.as_ref(py);
        
        if any.is_none() {
            Ok(Value::Null)
        } else if let Ok(b) = any.downcast::<PyBool>() {
            Ok(Value::Bool(b.is_true()))
        } else if let Ok(i) = any.downcast::<PyInt>() {
            Ok(Value::Number(i.extract::<i64>()?.into()))
        } else if let Ok(f) = any.downcast::<PyFloat>() {
            let val = f.value();
            if let Some(n) = serde_json::Number::from_f64(val) {
                Ok(Value::Number(n))
            } else {
                Ok(Value::Null)
            }
        } else if let Ok(s) = any.downcast::<PyString>() {
            Ok(Value::String(s.to_str()?.to_string()))
        } else if let Ok(list) = any.downcast::<PyList>() {
            let mut arr = Vec::new();
            for item in list.iter() {
                arr.push(depythonize(py, item.into())?);
            }
            Ok(Value::Array(arr))
        } else if let Ok(dict) = any.downcast::<PyDict>() {
            let mut map = serde_json::Map::new();
            for (key, value) in dict.iter() {
                let key_str = if let Ok(s) = key.downcast::<PyString>() {
                    s.to_str()?.to_string()
                } else {
                    key.str()?.to_str()?.to_string()
                };
                map.insert(key_str, depythonize(py, value.into())?);
            }
            Ok(Value::Object(map))
        } else {
            // Try to convert to string as fallback
            Ok(Value::String(any.str()?.to_str()?.to_string()))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_response_creation() {
        let response = Response::new(
            Some(b"Hello".to_vec()),
            Some(200),
            None,
            Some("text/plain".to_string()),
        );
        
        assert_eq!(response.status_code, 200);
        assert_eq!(response.content, b"Hello");
    }
    
    #[test]
    fn test_json_response() {
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let dict = pyo3::types::PyDict::new(py);
            dict.set_item("hello", "world").unwrap();
            
            let response = JSONResponse::new(py, dict.into(), Some(200), None).unwrap();
            
            assert_eq!(response.status_code, 200);
            assert_eq!(response.media_type, Some("application/json".to_string()));
        });
    }
}

