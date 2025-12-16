"""
Basic integration tests for Tachyon Engine
"""

import pytest
from tachyon_engine import (
    TachyonEngine,
    Route,
    Request,
    Response,
    JSONResponse,
    HTMLResponse,
    TestClient,
)


def test_tachyon_engine_creation():
    """Test creating a TachyonEngine instance"""
    app = TachyonEngine(debug=True)
    assert app is not None
    assert len(app.routes) == 0


def test_add_route():
    """Test adding a route to the engine"""
    app = TachyonEngine()
    
    async def homepage(request: Request):
        return JSONResponse({"message": "Hello, World!"})
    
    route = Route("/", homepage, methods=["GET"])
    app.add_route(route)
    
    assert len(app.routes) == 1
    assert app.routes[0].path == "/"


def test_json_response():
    """Test JSONResponse creation"""
    data = {"hello": "world", "number": 42}
    response = JSONResponse(data, status_code=200)
    
    assert response.status_code == 200
    assert response.media_type == "application/json"


def test_html_response():
    """Test HTMLResponse creation"""
    html = "<html><body>Hello</body></html>"
    response = HTMLResponse(html, status_code=200)
    
    assert response.status_code == 200
    assert response.media_type == "text/html"


def test_response_set_cookie():
    """Test setting cookies on response"""
    response = Response(b"test")
    response.set_cookie(
        "session_id",
        "abc123",
        max_age=3600,
        path="/",
        httponly=True,
        secure=True,
    )
    
    # Cookie should be set in headers
    assert response.headers.contains("set-cookie")


@pytest.mark.asyncio
async def test_basic_route_handler():
    """Test basic route handler execution"""
    app = TachyonEngine()
    
    async def test_endpoint(request: Request):
        return JSONResponse({"status": "ok"})
    
    route = Route("/test", test_endpoint, methods=["GET"])
    app.add_route(route)
    
    # Note: Full integration test would require running the app
    # This just tests the setup
    assert len(app.routes) == 1


def test_route_with_path_params():
    """Test route with path parameters"""
    app = TachyonEngine()
    
    async def user_detail(request: Request):
        return JSONResponse({"user_id": request.path_params.get("user_id")})
    
    route = Route("/users/{user_id}", user_detail, methods=["GET"])
    app.add_route(route)
    
    assert len(app.routes) == 1
    assert "{user_id}" in app.routes[0].path


def test_multiple_routes():
    """Test adding multiple routes"""
    app = TachyonEngine()
    
    async def home(request: Request):
        return JSONResponse({"page": "home"})
    
    async def about(request: Request):
        return JSONResponse({"page": "about"})
    
    async def contact(request: Request):
        return JSONResponse({"page": "contact"})
    
    app.add_route(Route("/", home, methods=["GET"]))
    app.add_route(Route("/about", about, methods=["GET"]))
    app.add_route(Route("/contact", contact, methods=["GET", "POST"]))
    
    assert len(app.routes) == 3


def test_route_with_multiple_methods():
    """Test route with multiple HTTP methods"""
    app = TachyonEngine()
    
    async def users_endpoint(request: Request):
        if request.method == "GET":
            return JSONResponse({"users": []})
        elif request.method == "POST":
            return JSONResponse({"created": True}, status_code=201)
    
    route = Route("/users", users_endpoint, methods=["GET", "POST"])
    app.add_route(route)
    
    assert "GET" in app.routes[0].methods
    assert "POST" in app.routes[0].methods


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

