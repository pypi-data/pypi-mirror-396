use pyo3::prelude::*;
use std::collections::HashMap;

/// Headers - Dict-like structure for HTTP headers
#[pyclass]
#[derive(Debug, Clone)]
pub struct Headers {
    inner: HashMap<String, String>,
}

#[pymethods]
impl Headers {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HashMap::new(),
        }
    }
    
    /// Get a header value by key (case-insensitive)
    pub fn get(&self, key: &str) -> Option<String> {
        let key_lower = key.to_lowercase();
        self.inner.get(&key_lower).cloned()
    }
    
    /// Set a header value
    pub fn set(&mut self, key: String, value: String) {
        let key_lower = key.to_lowercase();
        self.inner.insert(key_lower, value);
    }
    
    /// Check if header exists
    pub fn contains(&self, key: &str) -> bool {
        let key_lower = key.to_lowercase();
        self.inner.contains_key(&key_lower)
    }
    
    /// Get all headers as dict
    pub fn items(&self, py: Python) -> PyResult<PyObject> {
        let dict = pyo3::types::PyDict::new(py);
        for (key, value) in &self.inner {
            dict.set_item(key, value)?;
        }
        Ok(dict.into())
    }
    
    /// Get raw headers as list of tuples
    pub fn raw(&self, py: Python) -> PyResult<PyObject> {
        let list = pyo3::types::PyList::empty(py);
        for (key, value) in &self.inner {
            let tuple = pyo3::types::PyTuple::new(py, &[key, value]);
            list.append(tuple)?;
        }
        Ok(list.into())
    }
    
    fn __repr__(&self) -> String {
        format!("Headers({:?})", self.inner)
    }
    
    fn __str__(&self) -> String {
        format!("{:?}", self.inner)
    }
}

impl Headers {
    /// Create from ASGI headers (list of byte tuples)
    pub fn from_asgi_headers(headers: &[(bytes::Bytes, bytes::Bytes)]) -> Self {
        let mut inner = HashMap::new();
        
        for (key, value) in headers {
            if let (Ok(key_str), Ok(value_str)) = (
                String::from_utf8(key.to_vec()),
                String::from_utf8(value.to_vec()),
            ) {
                inner.insert(key_str.to_lowercase(), value_str);
            }
        }
        
        Self { inner }
    }
    
    /// Convert to raw byte tuples for ASGI
    pub fn to_asgi_headers(&self) -> Vec<(Vec<u8>, Vec<u8>)> {
        self.inner
            .iter()
            .map(|(k, v)| (k.as_bytes().to_vec(), v.as_bytes().to_vec()))
            .collect()
    }
    
    /// Get content type
    pub fn content_type(&self) -> Option<String> {
        self.get("content-type")
    }
    
    /// Get content length
    pub fn content_length(&self) -> Option<usize> {
        self.get("content-length")
            .and_then(|v| v.parse().ok())
    }
}

impl Default for Headers {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_headers_case_insensitive() {
        let mut headers = Headers::new();
        headers.set("Content-Type".to_string(), "application/json".to_string());
        
        assert_eq!(headers.get("content-type"), Some("application/json".to_string()));
        assert_eq!(headers.get("CONTENT-TYPE"), Some("application/json".to_string()));
        assert!(headers.contains("content-type"));
    }
    
    #[test]
    fn test_headers_from_asgi() {
        let asgi_headers = vec![
            (bytes::Bytes::from("content-type"), bytes::Bytes::from("text/html")),
            (bytes::Bytes::from("content-length"), bytes::Bytes::from("1234")),
        ];
        
        let headers = Headers::from_asgi_headers(&asgi_headers);
        assert_eq!(headers.get("content-type"), Some("text/html".to_string()));
        assert_eq!(headers.content_length(), Some(1234));
    }
}

