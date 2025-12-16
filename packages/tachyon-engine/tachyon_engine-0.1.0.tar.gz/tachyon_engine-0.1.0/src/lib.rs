use pyo3::prelude::*;

pub mod asgi;
pub mod application;
pub mod datastructures;
pub mod middleware;
pub mod request;
pub mod response;
pub mod routing;
pub mod server;
pub mod testclient;
pub mod websocket;
pub mod error;

use application::TachyonEngine;
use datastructures::{Headers, QueryParams, UploadFile};
use request::Request;
use response::{HTMLResponse, JSONResponse, Response};
use routing::{Route, WebSocketRoute};
use testclient::TestClient;
use websocket::WebSocket;

/// Tachyon Engine: High-performance ASGI framework written in Rust
#[pymodule]
fn _internal(_py: Python, m: &PyModule) -> PyResult<()> {
    // Application
    m.add_class::<TachyonEngine>()?;
    
    // Request/Response
    m.add_class::<Request>()?;
    m.add_class::<Response>()?;
    m.add_class::<JSONResponse>()?;
    m.add_class::<HTMLResponse>()?;
    
    // Routing
    m.add_class::<Route>()?;
    m.add_class::<WebSocketRoute>()?;
    
    // WebSocket
    m.add_class::<WebSocket>()?;
    
    // Data Structures
    m.add_class::<Headers>()?;
    m.add_class::<QueryParams>()?;
    m.add_class::<UploadFile>()?;
    
    // Testing
    m.add_class::<TestClient>()?;
    
    Ok(())
}

