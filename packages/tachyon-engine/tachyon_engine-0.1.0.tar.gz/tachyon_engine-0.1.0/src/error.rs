use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use std::fmt;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum TachyonError {
    #[error("ASGI protocol error: {0}")]
    AsgiProtocolError(String),
    
    #[error("Routing error: {0}")]
    RoutingError(String),
    
    #[error("Parse error: {0}")]
    ParseError(String),
    
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    
    #[error("JSON error: {0}")]
    JsonError(#[from] serde_json::Error),
    
    #[error("HTTP error: {0}")]
    HttpError(String),
    
    #[error("WebSocket error: {0}")]
    WebSocketError(String),
}

impl From<TachyonError> for PyErr {
    fn from(err: TachyonError) -> PyErr {
        PyException::new_err(err.to_string())
    }
}

impl From<PyErr> for TachyonError {
    fn from(err: PyErr) -> TachyonError {
        TachyonError::AsgiProtocolError(format!("Python error: {}", err))
    }
}

pub type Result<T> = std::result::Result<T, TachyonError>;

