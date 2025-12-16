use bytes::Bytes;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString};
use std::collections::HashMap;

use super::AsgiVersion;
use crate::error::{Result, TachyonError};

/// ASGI Scope types
#[derive(Debug, Clone, PartialEq)]
pub enum ScopeType {
    Http,
    WebSocket,
    Lifespan,
}

impl ScopeType {
    pub fn as_str(&self) -> &str {
        match self {
            ScopeType::Http => "http",
            ScopeType::WebSocket => "websocket",
            ScopeType::Lifespan => "lifespan",
        }
    }
    
    pub fn from_str(s: &str) -> Result<Self> {
        match s {
            "http" => Ok(ScopeType::Http),
            "websocket" => Ok(ScopeType::WebSocket),
            "lifespan" => Ok(ScopeType::Lifespan),
            _ => Err(TachyonError::AsgiProtocolError(format!(
                "Invalid scope type: {}",
                s
            ))),
        }
    }
}

/// ASGI Scope - Contains all metadata about the connection
#[derive(Debug, Clone)]
pub struct AsgiScope {
    pub scope_type: ScopeType,
    pub asgi: AsgiVersion,
    pub http_version: String,
    pub method: String,
    pub scheme: String,
    pub path: String,
    pub raw_path: Bytes,
    pub query_string: Bytes,
    pub root_path: String,
    pub headers: Vec<(Bytes, Bytes)>,
    pub server: Option<(String, u16)>,
    pub client: Option<(String, u16)>,
    pub extensions: HashMap<String, PyObject>,
}

impl AsgiScope {
    /// Create scope from Python dict
    pub fn from_py_dict(py: Python, scope: &PyDict) -> Result<Self> {
        let scope_type_str = scope
            .get_item("type")?
            .ok_or_else(|| TachyonError::AsgiProtocolError("Missing 'type' in scope".to_string()))?
            .extract::<String>()?;
        
        let scope_type = ScopeType::from_str(&scope_type_str)?;
        
        let method = scope
            .get_item("method")?
            .and_then(|v| v.extract::<String>().ok())
            .unwrap_or_else(|| "GET".to_string());
        
        let path = scope
            .get_item("path")?
            .and_then(|v| v.extract::<String>().ok())
            .unwrap_or_else(|| "/".to_string());
        
        let path_bytes = path.as_bytes().to_vec();
        let raw_path = scope
            .get_item("raw_path")?
            .and_then(|v| v.extract::<Vec<u8>>().ok())
            .map(Bytes::from)
            .unwrap_or_else(|| Bytes::from(path_bytes));
        
        let query_string = scope
            .get_item("query_string")?
            .and_then(|v| v.extract::<Vec<u8>>().ok())
            .map(Bytes::from)
            .unwrap_or_else(|| Bytes::new());
        
        let headers = scope
            .get_item("headers")?
            .map(|h| super::py_headers_to_vec(py, h))
            .transpose()?
            .unwrap_or_default();
        
        let http_version = scope
            .get_item("http_version")?
            .and_then(|v| v.extract::<String>().ok())
            .unwrap_or_else(|| "1.1".to_string());
        
        let scheme = scope
            .get_item("scheme")?
            .and_then(|v| v.extract::<String>().ok())
            .unwrap_or_else(|| "http".to_string());
        
        let root_path = scope
            .get_item("root_path")?
            .and_then(|v| v.extract::<String>().ok())
            .unwrap_or_default();
        
        let server = scope
            .get_item("server")?
            .and_then(|v| {
                let tuple = v.downcast::<pyo3::types::PyTuple>().ok()?;
                let host = tuple.get_item(0).ok()?.extract::<String>().ok()?;
                let port = tuple.get_item(1).ok()?.extract::<u16>().ok()?;
                Some((host, port))
            });
        
        let client = scope
            .get_item("client")?
            .and_then(|v| {
                let tuple = v.downcast::<pyo3::types::PyTuple>().ok()?;
                let host = tuple.get_item(0).ok()?.extract::<String>().ok()?;
                let port = tuple.get_item(1).ok()?.extract::<u16>().ok()?;
                Some((host, port))
            });
        
        Ok(Self {
            scope_type,
            asgi: AsgiVersion::default(),
            http_version,
            method,
            scheme,
            path,
            raw_path,
            query_string,
            root_path,
            headers,
            server,
            client,
            extensions: HashMap::new(),
        })
    }
    
    /// Convert to Python dict
    pub fn to_py_dict(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        
        dict.set_item("type", self.scope_type.as_str())?;
        dict.set_item("asgi", self.asgi.to_py_dict(py)?)?;
        dict.set_item("http_version", &self.http_version)?;
        dict.set_item("method", &self.method)?;
        dict.set_item("scheme", &self.scheme)?;
        dict.set_item("path", &self.path)?;
        dict.set_item("raw_path", self.raw_path.as_ref())?;
        dict.set_item("query_string", self.query_string.as_ref())?;
        dict.set_item("root_path", &self.root_path)?;
        
        // Convert headers
        let headers_list = pyo3::types::PyList::empty(py);
        for (key, value) in &self.headers {
            let tuple = pyo3::types::PyTuple::new(
                py,
                &[key.as_ref(), value.as_ref()],
            );
            headers_list.append(tuple)?;
        }
        dict.set_item("headers", headers_list)?;
        
        if let Some((host, port)) = &self.server {
            let tuple = pyo3::types::PyTuple::new(py, &[host.as_str(), &port.to_string()]);
            dict.set_item("server", tuple)?;
        }
        
        if let Some((host, port)) = &self.client {
            let tuple = pyo3::types::PyTuple::new(py, &[host.as_str(), &port.to_string()]);
            dict.set_item("client", tuple)?;
        }
        
        Ok(dict.into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_scope_type_conversion() {
        assert_eq!(ScopeType::from_str("http").unwrap(), ScopeType::Http);
        assert_eq!(ScopeType::from_str("websocket").unwrap(), ScopeType::WebSocket);
        assert_eq!(ScopeType::from_str("lifespan").unwrap(), ScopeType::Lifespan);
        assert!(ScopeType::from_str("invalid").is_err());
    }
}

