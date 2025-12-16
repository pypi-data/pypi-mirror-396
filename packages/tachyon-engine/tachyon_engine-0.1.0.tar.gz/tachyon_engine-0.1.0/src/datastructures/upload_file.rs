use pyo3::prelude::*;
use std::path::PathBuf;
use tokio::fs::File;
use tokio::io::{AsyncReadExt, AsyncSeekExt, AsyncWriteExt};

/// UploadFile - Wrapper for uploaded files
#[pyclass]
pub struct UploadFile {
    #[pyo3(get)]
    filename: String,
    
    #[pyo3(get)]
    content_type: Option<String>,
    
    #[pyo3(get)]
    size: Option<usize>,
    
    content: Vec<u8>,
    position: usize,
}

#[pymethods]
impl UploadFile {
    #[new]
    #[pyo3(signature = (filename, content_type=None, content=Vec::new()))]
    pub fn new(
        filename: String,
        content_type: Option<String>,
        content: Vec<u8>,
    ) -> Self {
        let size = Some(content.len());
        Self {
            filename,
            content_type,
            size,
            content,
            position: 0,
        }
    }
    
    /// Read file content
    pub fn read<'py>(&mut self, py: Python<'py>) -> PyResult<&'py pyo3::types::PyBytes> {
        let data = &self.content[self.position..];
        self.position = self.content.len();
        Ok(pyo3::types::PyBytes::new(py, data))
    }
    
    /// Read n bytes
    pub fn read_bytes<'py>(
        &mut self,
        py: Python<'py>,
        n: usize,
    ) -> PyResult<&'py pyo3::types::PyBytes> {
        let end = std::cmp::min(self.position + n, self.content.len());
        let data = &self.content[self.position..end];
        self.position = end;
        Ok(pyo3::types::PyBytes::new(py, data))
    }
    
    /// Seek to position
    pub fn seek(&mut self, position: usize) -> PyResult<()> {
        if position <= self.content.len() {
            self.position = position;
            Ok(())
        } else {
            Err(pyo3::exceptions::PyValueError::new_err(
                "Position out of bounds",
            ))
        }
    }
    
    /// Close file (no-op for in-memory)
    pub fn close(&mut self) -> PyResult<()> {
        Ok(())
    }
    
    /// Write to file on disk
    pub fn save(&self, path: String) -> PyResult<()> {
        std::fs::write(path, &self.content)?;
        Ok(())
    }
    
    fn __repr__(&self) -> String {
        format!(
            "UploadFile(filename='{}', content_type={:?}, size={:?})",
            self.filename, self.content_type, self.size
        )
    }
}

impl UploadFile {
    /// Create from raw bytes
    pub fn from_bytes(
        filename: String,
        content_type: Option<String>,
        content: Vec<u8>,
    ) -> Self {
        Self::new(filename, content_type, content)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_upload_file_read() {
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let mut file = UploadFile::new(
                "test.txt".to_string(),
                Some("text/plain".to_string()),
                b"Hello, World!".to_vec(),
            );
            
            let data = file.read(py).unwrap();
            assert_eq!(data.as_bytes(), b"Hello, World!");
        });
    }
    
    #[test]
    fn test_upload_file_seek() {
        let mut file = UploadFile::new(
            "test.txt".to_string(),
            None,
            b"Hello, World!".to_vec(),
        );
        
        file.seek(7).unwrap();
        assert_eq!(file.position, 7);
    }
}

