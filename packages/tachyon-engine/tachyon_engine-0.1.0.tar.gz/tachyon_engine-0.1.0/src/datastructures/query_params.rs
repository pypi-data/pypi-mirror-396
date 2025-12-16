use pyo3::prelude::*;
use std::collections::HashMap;

/// QueryParams - Dict-like structure for URL query parameters
#[pyclass]
#[derive(Debug, Clone)]
pub struct QueryParams {
    inner: HashMap<String, Vec<String>>,
}

#[pymethods]
impl QueryParams {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: HashMap::new(),
        }
    }
    
    /// Get first value for a key
    pub fn get(&self, key: &str) -> Option<String> {
        self.inner.get(key).and_then(|v| v.first().cloned())
    }
    
    /// Get all values for a key
    pub fn get_list(&self, key: &str) -> Vec<String> {
        self.inner.get(key).cloned().unwrap_or_default()
    }
    
    /// Get all params as dict
    pub fn items(&self, py: Python) -> PyResult<PyObject> {
        let dict = pyo3::types::PyDict::new(py);
        for (key, values) in &self.inner {
            if values.len() == 1 {
                dict.set_item(key, &values[0])?;
            } else {
                let list = pyo3::types::PyList::new(py, values);
                dict.set_item(key, list)?;
            }
        }
        Ok(dict.into())
    }
    
    /// Check if key exists
    pub fn contains(&self, key: &str) -> bool {
        self.inner.contains_key(key)
    }
    
    fn __repr__(&self) -> String {
        format!("QueryParams({:?})", self.inner)
    }
    
    fn __str__(&self) -> String {
        format!("{:?}", self.inner)
    }
}

impl QueryParams {
    /// Parse query string
    pub fn from_query_string(query_string: &[u8]) -> Self {
        let mut inner: HashMap<String, Vec<String>> = HashMap::new();
        
        let query_str = String::from_utf8_lossy(query_string);
        
        for pair in query_str.split('&') {
            if pair.is_empty() {
                continue;
            }
            
            let mut parts = pair.splitn(2, '=');
            let key = parts.next().unwrap_or("");
            let value = parts.next().unwrap_or("");
            
            // URL decode
            let key_decoded = urlencoding::decode(key).unwrap_or_default().to_string();
            let value_decoded = urlencoding::decode(value).unwrap_or_default().to_string();
            
            inner
                .entry(key_decoded)
                .or_insert_with(Vec::new)
                .push(value_decoded);
        }
        
        Self { inner }
    }
}

impl Default for QueryParams {
    fn default() -> Self {
        Self::new()
    }
}

// URL encoding utilities
mod urlencoding {
    pub fn decode(s: &str) -> Option<String> {
        let mut result = String::new();
        let mut chars = s.chars().peekable();
        
        while let Some(ch) = chars.next() {
            match ch {
                '%' => {
                    let hex1 = chars.next()?;
                    let hex2 = chars.next()?;
                    let hex_str = format!("{}{}", hex1, hex2);
                    let byte = u8::from_str_radix(&hex_str, 16).ok()?;
                    result.push(byte as char);
                }
                '+' => result.push(' '),
                _ => result.push(ch),
            }
        }
        
        Some(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_query_params_parse() {
        let params = QueryParams::from_query_string(b"foo=bar&baz=qux");
        assert_eq!(params.get("foo"), Some("bar".to_string()));
        assert_eq!(params.get("baz"), Some("qux".to_string()));
    }
    
    #[test]
    fn test_query_params_multiple_values() {
        let params = QueryParams::from_query_string(b"foo=bar&foo=baz");
        assert_eq!(params.get("foo"), Some("bar".to_string()));
        assert_eq!(params.get_list("foo"), vec!["bar".to_string(), "baz".to_string()]);
    }
    
    #[test]
    fn test_query_params_url_decode() {
        let params = QueryParams::from_query_string(b"name=John+Doe&email=test%40example.com");
        assert_eq!(params.get("name"), Some("John Doe".to_string()));
        assert_eq!(params.get("email"), Some("test@example.com".to_string()));
    }
}

