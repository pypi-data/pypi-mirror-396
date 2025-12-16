"""
Tests for routing functionality
"""

import pytest
from tachyon_engine import TachyonEngine, Route, Request, JSONResponse


def test_route_creation():
    """Test creating a Route"""
    async def handler(request: Request):
        return JSONResponse({"status": "ok"})
    
    route = Route("/test", handler, methods=["GET"], name="test_route")
    
    assert route.path == "/test"
    assert "GET" in route.methods
    assert route.name == "test_route"


def test_route_default_method():
    """Test Route with default GET method"""
    async def handler(request: Request):
        return JSONResponse({"status": "ok"})
    
    route = Route("/test", handler)
    
    assert "GET" in route.methods


def test_route_multiple_methods():
    """Test Route with multiple methods"""
    async def handler(request: Request):
        return JSONResponse({"status": "ok"})
    
    route = Route("/test", handler, methods=["GET", "POST", "PUT"])
    
    assert len(route.methods) == 3
    assert "GET" in route.methods
    assert "POST" in route.methods
    assert "PUT" in route.methods


def test_route_with_path_parameters():
    """Test route with path parameters"""
    async def handler(request: Request):
        user_id = request.path_params.get("user_id")
        return JSONResponse({"user_id": user_id})
    
    route = Route("/users/{user_id}", handler, methods=["GET"])
    
    assert "{user_id}" in route.path


def test_nested_path_parameters():
    """Test route with nested path parameters"""
    async def handler(request: Request):
        return JSONResponse({
            "post_id": request.path_params.get("post_id"),
            "comment_id": request.path_params.get("comment_id"),
        })
    
    route = Route(
        "/posts/{post_id}/comments/{comment_id}",
        handler,
        methods=["GET"],
    )
    
    assert "{post_id}" in route.path
    assert "{comment_id}" in route.path


def test_add_multiple_routes_to_app():
    """Test adding multiple routes to application"""
    app = TachyonEngine()
    
    async def home(request: Request):
        return JSONResponse({"page": "home"})
    
    async def api(request: Request):
        return JSONResponse({"page": "api"})
    
    app.add_route(Route("/", home))
    app.add_route(Route("/api", api))
    
    assert len(app.routes) == 2
    paths = [r.path for r in app.routes]
    assert "/" in paths
    assert "/api" in paths


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

