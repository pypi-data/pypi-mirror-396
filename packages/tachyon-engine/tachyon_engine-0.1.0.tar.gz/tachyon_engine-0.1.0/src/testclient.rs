use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};
use reqwest;
use std::collections::HashMap;

use crate::application::TachyonEngine;

/// TestClient - HTTP client for testing ASGI applications
#[pyclass(unsendable)]
#[derive(Clone)]
pub struct TestClient {
    app: Py<TachyonEngine>,
    base_url: String,
    client: reqwest::Client,
    cookies: HashMap<String, String>,
}

#[pymethods]
impl TestClient {
    #[new]
    #[pyo3(signature = (app, base_url=None))]
    pub fn new(app: Py<TachyonEngine>, base_url: Option<String>) -> Self {
        Self {
            app,
            base_url: base_url.unwrap_or_else(|| "http://testserver".to_string()),
            client: reqwest::Client::new(),
            cookies: HashMap::new(),
        }
    }
    
    /// Send GET request
    #[pyo3(signature = (url, params=None, headers=None))]
    pub fn get(
        &mut self,
        py: Python,
        url: String,
        params: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
    ) -> PyResult<TestResponse> {
        self.request(py, "GET", url, params, headers, None, None)
    }
    
    /// Send POST request
    #[pyo3(signature = (url, json=None, data=None, headers=None))]
    pub fn post(
        &mut self,
        py: Python,
        url: String,
        json: Option<PyObject>,
        data: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
    ) -> PyResult<TestResponse> {
        self.request(py, "POST", url, None, headers, json, data)
    }
    
    /// Send PUT request
    #[pyo3(signature = (url, json=None, data=None, headers=None))]
    pub fn put(
        &mut self,
        py: Python,
        url: String,
        json: Option<PyObject>,
        data: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
    ) -> PyResult<TestResponse> {
        self.request(py, "PUT", url, None, headers, json, data)
    }
    
    /// Send DELETE request
    #[pyo3(signature = (url, headers=None))]
    pub fn delete(
        &mut self,
        py: Python,
        url: String,
        headers: Option<HashMap<String, String>>,
    ) -> PyResult<TestResponse> {
        self.request(py, "DELETE", url, None, headers, None, None)
    }
    
    /// Send PATCH request
    #[pyo3(signature = (url, json=None, data=None, headers=None))]
    pub fn patch(
        &mut self,
        py: Python,
        url: String,
        json: Option<PyObject>,
        data: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
    ) -> PyResult<TestResponse> {
        self.request(py, "PATCH", url, None, headers, json, data)
    }
    
    fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }
    
    fn __exit__(
        &mut self,
        _exc_type: PyObject,
        _exc_value: PyObject,
        _traceback: PyObject,
    ) -> PyResult<bool> {
        Ok(false)
    }
}

impl TestClient {
    /// Internal request method
    fn request(
        &mut self,
        py: Python,
        method: &str,
        url: String,
        params: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
        _json: Option<PyObject>,
        _data: Option<HashMap<String, String>>,
    ) -> PyResult<TestResponse> {
        // Build full URL
        let _full_url = if url.starts_with("http") {
            url.clone()
        } else {
            format!("{}{}", self.base_url, url.clone())
        };
        
        // Call the ASGI app directly
        let app = self.app.borrow(py);
        
        // Build ASGI scope
        let scope = self.build_scope(py, method, &url, params, headers.clone())?;
        
        // Create receive and send callables
        let (receive, send) = self.create_asgi_channels(py, _json, _data)?;
        
        // Call the app
        let _result = app.__call__(py, scope, receive, send)?;
        
        // Wait for result and build response
        // For now, return a mock response
        Ok(TestResponse {
            status_code: 200,
            headers: HashMap::new(),
            content: Vec::new(),
        })
    }
    
    fn build_scope(
        &self,
        py: Python,
        method: &str,
        path: &str,
        _params: Option<HashMap<String, String>>,
        headers: Option<HashMap<String, String>>,
    ) -> PyResult<PyObject> {
        let scope = PyDict::new(py);
        
        scope.set_item("type", "http")?;
        scope.set_item("method", method)?;
        scope.set_item("path", path)?;
        scope.set_item("query_string", b"")?;
        scope.set_item("root_path", "")?;
        
        // Add headers
        let headers_list = pyo3::types::PyList::empty(py);
        if let Some(h) = headers {
            for (key, value) in h {
                let tuple = pyo3::types::PyTuple::new(
                    py,
                    &[key.as_bytes(), value.as_bytes()],
                );
                headers_list.append(tuple)?;
            }
        }
        scope.set_item("headers", headers_list)?;
        
        // ASGI version
        let asgi = PyDict::new(py);
        asgi.set_item("version", "3.0")?;
        scope.set_item("asgi", asgi)?;
        
        Ok(scope.into())
    }
    
    fn create_asgi_channels(
        &self,
        py: Python,
        _json: Option<PyObject>,
        _data: Option<HashMap<String, String>>,
    ) -> PyResult<(PyObject, PyObject)> {
        // Create mock receive callable
        let receive = pyo3::types::PyModule::from_code(
            py,
            r#"
async def receive():
    return {"type": "http.request", "body": b"", "more_body": False}
"#,
            "",
            "",
        )?
        .getattr("receive")?
        .into();
        
        // Create mock send callable
        let send = pyo3::types::PyModule::from_code(
            py,
            r#"
async def send(message):
    pass
"#,
            "",
            "",
        )?
        .getattr("send")?
        .into();
        
        Ok((receive, send))
    }
}

/// TestResponse - Response from TestClient
#[pyclass]
#[derive(Clone)]
pub struct TestResponse {
    #[pyo3(get)]
    pub status_code: u16,
    
    headers: HashMap<String, String>,
    content: Vec<u8>,
}

#[pymethods]
impl TestResponse {
    /// Get response body as bytes
    pub fn content<'py>(&self, py: Python<'py>) -> &'py PyBytes {
        PyBytes::new(py, &self.content)
    }
    
    /// Get response body as text
    pub fn text(&self) -> PyResult<String> {
        String::from_utf8(self.content.clone())
            .map_err(|e| pyo3::exceptions::PyUnicodeDecodeError::new_err(e.to_string()))
    }
    
    /// Parse response as JSON
    pub fn json(&self, py: Python) -> PyResult<PyObject> {
        let json_value: serde_json::Value = serde_json::from_slice(&self.content)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
        
        crate::request::pythonize::pythonize(py, &json_value)
    }
    
    /// Get headers
    #[getter]
    pub fn headers(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        for (key, value) in &self.headers {
            dict.set_item(key, value)?;
        }
        Ok(dict.into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    // TestClient tests require full integration
}

