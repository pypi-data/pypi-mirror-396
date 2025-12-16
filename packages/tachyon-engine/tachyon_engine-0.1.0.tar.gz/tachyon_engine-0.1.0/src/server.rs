use hyper::service::{make_service_fn, service_fn};
use hyper::{Body, Request as HyperRequest, Response as HyperResponse, Server, StatusCode};
use pyo3::prelude::*;
use std::convert::Infallible;
use std::net::SocketAddr;
use std::sync::Arc;

use crate::application::TachyonEngine;
use crate::error::Result;

/// Start HTTP server with Hyper + Tokio
pub async fn serve(
    app: Arc<TachyonEngine>,
    host: String,
    port: u16,
) -> Result<()> {
    let addr: SocketAddr = format!("{}:{}", host, port)
        .parse()
        .map_err(|e| crate::error::TachyonError::IoError(
            std::io::Error::new(std::io::ErrorKind::InvalidInput, format!("Invalid address: {}", e))
        ))?;
    
    println!("🚀 Tachyon Engine running on http://{}:{}", host, port);
    
    let make_svc = make_service_fn(move |_conn| {
        let app = Arc::clone(&app);
        async move {
            Ok::<_, Infallible>(service_fn(move |req| {
                let app = Arc::clone(&app);
                async move {
                    handle_request(app, req).await
                }
            }))
        }
    });
    
    let server = Server::bind(&addr).serve(make_svc);
    
    server.await
        .map_err(|e| crate::error::TachyonError::IoError(
            std::io::Error::new(std::io::ErrorKind::Other, e)
        ))?;
    
    Ok(())
}

/// Handle incoming HTTP request
async fn handle_request(
    _app: Arc<TachyonEngine>,
    _req: HyperRequest<Body>,
) -> std::result::Result<HyperResponse<Body>, Infallible> {
    // Convert Hyper request to ASGI scope
    Python::with_gil(|_py| {
        // TODO: Full ASGI conversion and handling
        // For now, return a simple response
        
        let response = HyperResponse::builder()
            .status(StatusCode::OK)
            .body(Body::from("Hello from Tachyon Engine!"))
            .unwrap();
        
        Ok(response)
    })
}

/// Convert Hyper request to ASGI scope
fn hyper_to_asgi_scope(
    py: Python,
    req: &HyperRequest<Body>,
) -> PyResult<PyObject> {
    use pyo3::types::{PyDict, PyList, PyTuple};
    
    let scope = PyDict::new(py);
    
    // Type
    scope.set_item("type", "http")?;
    
    // ASGI version
    let asgi = PyDict::new(py);
    asgi.set_item("version", "3.0")?;
    asgi.set_item("spec_version", "2.3")?;
    scope.set_item("asgi", asgi)?;
    
    // HTTP version
    let http_version = match req.version() {
        hyper::Version::HTTP_09 => "0.9",
        hyper::Version::HTTP_10 => "1.0",
        hyper::Version::HTTP_11 => "1.1",
        hyper::Version::HTTP_2 => "2",
        hyper::Version::HTTP_3 => "3",
        _ => "1.1",
    };
    scope.set_item("http_version", http_version)?;
    
    // Method
    scope.set_item("method", req.method().as_str())?;
    
    // Path
    let path = req.uri().path();
    scope.set_item("path", path)?;
    scope.set_item("raw_path", path.as_bytes())?;
    
    // Query string
    let query_string = req.uri().query().unwrap_or("").as_bytes();
    scope.set_item("query_string", query_string)?;
    
    // Headers
    let headers = PyList::empty(py);
    for (name, value) in req.headers() {
        let tuple = PyTuple::new(
            py,
            &[
                name.as_str().as_bytes(),
                value.as_bytes(),
            ],
        );
        headers.append(tuple)?;
    }
    scope.set_item("headers", headers)?;
    
    // Server (TODO: Get actual server address)
    let server_tuple = PyTuple::new(py, &["127.0.0.1", "8000"]);
    scope.set_item("server", server_tuple)?;
    
    // Scheme
    let scheme = req.uri().scheme_str().unwrap_or("http");
    scope.set_item("scheme", scheme)?;
    
    // Root path
    scope.set_item("root_path", "")?;
    
    Ok(scope.into())
}

#[cfg(test)]
mod tests {
    use super::*;
    
    // Server tests require integration testing
}

