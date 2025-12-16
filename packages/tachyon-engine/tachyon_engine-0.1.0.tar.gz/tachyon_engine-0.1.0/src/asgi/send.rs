use pyo3::prelude::*;
use pyo3::types::PyDict;

/// ASGI Send callable wrapper
#[derive(Clone)]
pub struct AsgiSend {
    callable: PyObject,
}

impl AsgiSend {
    pub fn new(callable: PyObject) -> Self {
        Self { callable }
    }
    
    /// Send a message to the ASGI server
    pub async fn send(&self, py: Python<'_>, message: PyObject) -> PyResult<()> {
        // Call the async callable with the message
        let coroutine = self.callable.call1(py, (message,))?;
        
        // Await the coroutine
        pyo3_asyncio::tokio::into_future(coroutine.as_ref(py))?;
        
        Ok(())
    }
    
    /// Send HTTP response start
    pub async fn send_response_start(
        &self,
        py: Python<'_>,
        status: u16,
        headers: Vec<(Vec<u8>, Vec<u8>)>,
    ) -> PyResult<()> {
        let dict = PyDict::new(py);
        dict.set_item("type", "http.response.start")?;
        dict.set_item("status", status)?;
        
        let headers_list = pyo3::types::PyList::empty(py);
        for (key, value) in headers {
            let tuple = pyo3::types::PyTuple::new(py, &[key, value]);
            headers_list.append(tuple)?;
        }
        dict.set_item("headers", headers_list)?;
        
        self.send(py, dict.into()).await
    }
    
    /// Send HTTP response body
    pub async fn send_response_body(
        &self,
        py: Python<'_>,
        body: Vec<u8>,
        more_body: bool,
    ) -> PyResult<()> {
        let dict = PyDict::new(py);
        dict.set_item("type", "http.response.body")?;
        dict.set_item("body", body)?;
        dict.set_item("more_body", more_body)?;
        
        self.send(py, dict.into()).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    // Tests will be added when we have async test setup
}

