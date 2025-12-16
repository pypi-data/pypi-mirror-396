pub mod matcher;
pub mod route;
pub mod websocket_route;

pub use matcher::PathMatcher;
pub use route::Route;
pub use websocket_route::WebSocketRoute;

use std::collections::HashMap;
use crate::error::{Result, TachyonError};

/// Router - Maps paths to handlers
pub struct Router {
    routes: Vec<Route>,
    matcher: PathMatcher,
}

impl Router {
    pub fn new() -> Self {
        Self {
            routes: Vec::new(),
            matcher: PathMatcher::new(),
        }
    }
    
    /// Add a route
    pub fn add_route(&mut self, route: Route) -> Result<()> {
        self.matcher.add_route(&route.path, route.methods.clone())?;
        self.routes.push(route);
        Ok(())
    }
    
    /// Match a request to a route
    pub fn match_route(
        &self,
        path: &str,
        method: &str,
    ) -> Option<(&Route, HashMap<String, String>)> {
        let (route_path, params) = self.matcher.match_path(path, method)?;
        
        // Find the route with matching path
        let route = self.routes.iter().find(|r| r.path == route_path)?;
        
        Some((route, params))
    }
    
    /// Get all routes
    pub fn routes(&self) -> &[Route] {
        &self.routes
    }
}

impl Default for Router {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_router_add_and_match() {
        pyo3::prepare_freethreaded_python();
        
        Python::with_gil(|py| {
            let mut router = Router::new();
            
            let handler = py.None();
            let route = Route::new(
                "/users/:user_id".to_string(),
                handler,
                vec!["GET".to_string()],
                None,
            );
            
            router.add_route(route).unwrap();
            
            let (matched_route, params) = router.match_route("/users/123", "GET").unwrap();
            assert_eq!(matched_route.path, "/users/:user_id");
            assert_eq!(params.get("user_id"), Some(&"123".to_string()));
        });
    }
}

use pyo3::prelude::*;

