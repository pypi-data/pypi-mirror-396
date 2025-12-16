pub mod receive;
pub mod scope;
pub mod send;

pub use receive::AsgiReceive;
pub use scope::{AsgiScope, ScopeType};
pub use send::AsgiSend;

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyString};
use std::collections::HashMap;

/// ASGI Version information
#[derive(Debug, Clone)]
pub struct AsgiVersion {
    pub version: String,
    pub spec_version: String,
}

impl Default for AsgiVersion {
    fn default() -> Self {
        Self {
            version: "3.0".to_string(),
            spec_version: "2.3".to_string(),
        }
    }
}

impl AsgiVersion {
    pub fn to_py_dict(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("version", &self.version)?;
        dict.set_item("spec_version", &self.spec_version)?;
        Ok(dict.into())
    }
}

/// Convert Python dict to Rust HashMap for headers
pub fn py_headers_to_vec(_py: Python, headers: &PyAny) -> PyResult<Vec<(bytes::Bytes, bytes::Bytes)>> {
    let mut result = Vec::new();
    
    if let Ok(list) = headers.downcast::<pyo3::types::PyList>() {
        for item in list.iter() {
            if let Ok(tuple) = item.downcast::<pyo3::types::PyTuple>() {
                if tuple.len() == 2 {
                    let key = tuple.get_item(0)?;
                    let value = tuple.get_item(1)?;
                    
                    let key_bytes = if let Ok(s) = key.downcast::<PyString>() {
                        bytes::Bytes::from(s.to_str()?.as_bytes().to_vec())
                    } else if let Ok(b) = key.downcast::<PyBytes>() {
                        bytes::Bytes::from(b.as_bytes().to_vec())
                    } else {
                        continue;
                    };
                    
                    let value_bytes = if let Ok(s) = value.downcast::<PyString>() {
                        bytes::Bytes::from(s.to_str()?.as_bytes().to_vec())
                    } else if let Ok(b) = value.downcast::<PyBytes>() {
                        bytes::Bytes::from(b.as_bytes().to_vec())
                    } else {
                        continue;
                    };
                    
                    result.push((key_bytes, value_bytes));
                }
            }
        }
    }
    
    Ok(result)
}

