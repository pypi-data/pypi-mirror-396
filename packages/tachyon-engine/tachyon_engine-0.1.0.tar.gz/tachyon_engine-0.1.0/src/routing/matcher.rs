use matchit::Router as MatchitRouter;
use std::collections::HashMap;

use crate::error::{Result, TachyonError};

/// PathMatcher - Efficient path matching with parameter extraction
pub struct PathMatcher {
    // One router per HTTP method
    routers: HashMap<String, MatchitRouter<String>>,
}

impl PathMatcher {
    pub fn new() -> Self {
        Self {
            routers: HashMap::new(),
        }
    }
    
    /// Add a route pattern
    pub fn add_route(&mut self, path: &str, methods: Vec<String>) -> Result<()> {
        for method in methods {
            let router = self.routers
                .entry(method.to_uppercase())
                .or_insert_with(MatchitRouter::new);
            
            router
                .insert(path, path.to_string())
                .map_err(|e| TachyonError::RoutingError(format!(
                    "Failed to add route {}: {}",
                    path, e
                )))?;
        }
        
        Ok(())
    }
    
    /// Match a path and extract parameters
    pub fn match_path(
        &self,
        path: &str,
        method: &str,
    ) -> Option<(String, HashMap<String, String>)> {
        let router = self.routers.get(&method.to_uppercase())?;
        
        let matched = router.at(path).ok()?;
        
        let params: HashMap<String, String> = matched
            .params
            .iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect();
        
        Some((matched.value.clone(), params))
    }
}

impl Default for PathMatcher {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_path_matcher() {
        let mut matcher = PathMatcher::new();
        
        matcher.add_route("/users/:id", vec!["GET".to_string()]).unwrap();
        matcher.add_route("/posts/:post_id/comments/:comment_id", vec!["GET".to_string()]).unwrap();
        
        let (path, params) = matcher.match_path("/users/123", "GET").unwrap();
        assert_eq!(path, "/users/:id");
        assert_eq!(params.get("id"), Some(&"123".to_string()));
        
        let (path, params) = matcher.match_path("/posts/42/comments/99", "GET").unwrap();
        assert_eq!(path, "/posts/:post_id/comments/:comment_id");
        assert_eq!(params.get("post_id"), Some(&"42".to_string()));
        assert_eq!(params.get("comment_id"), Some(&"99".to_string()));
    }
    
    #[test]
    fn test_method_matching() {
        let mut matcher = PathMatcher::new();
        
        matcher.add_route("/users", vec!["GET".to_string(), "POST".to_string()]).unwrap();
        
        assert!(matcher.match_path("/users", "GET").is_some());
        assert!(matcher.match_path("/users", "POST").is_some());
        assert!(matcher.match_path("/users", "DELETE").is_none());
    }
}

