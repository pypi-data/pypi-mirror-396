use pyo3::prelude::*;
use pyo3::types::PyDict;

/// ASGI Receive callable wrapper
#[derive(Clone)]
pub struct AsgiReceive {
    callable: PyObject,
}

impl AsgiReceive {
    pub fn new(callable: PyObject) -> Self {
        Self { callable }
    }
    
    /// Receive a message from the ASGI server
    pub async fn receive(&self, py: Python<'_>) -> PyResult<PyObject> {
        // Call the async callable
        let coroutine = self.callable.call0(py)?;
        
        // Note: Full async implementation requires more complex setup
        // For now, return the coroutine object
        Ok(coroutine)
    }
    
    /// Receive and parse HTTP body
    pub async fn receive_body(&self, py: Python<'_>) -> PyResult<Vec<u8>> {
        let mut body = Vec::new();
        
        loop {
            let message = self.receive(py).await?;
            let dict = message.downcast::<PyDict>(py)?;
            
            let msg_type = dict
                .get_item("type")?
                .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Missing 'type' in message"))?
                .extract::<String>()?;
            
            if msg_type == "http.request" {
                if let Some(body_bytes) = dict.get_item("body")? {
                    let chunk = body_bytes.extract::<Vec<u8>>()?;
                    body.extend_from_slice(&chunk);
                }
                
                let more_body = dict
                    .get_item("more_body")?
                    .and_then(|v| v.extract::<bool>().ok())
                    .unwrap_or(false);
                
                if !more_body {
                    break;
                }
            } else if msg_type == "http.disconnect" {
                break;
            }
        }
        
        Ok(body)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    // Tests will be added when we have async test setup
}

