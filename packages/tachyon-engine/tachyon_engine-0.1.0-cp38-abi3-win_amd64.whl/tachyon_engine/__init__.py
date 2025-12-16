"""
Tachyon Engine - High-performance ASGI framework
"""

try:
    from tachyon_engine._internal import (
        TachyonEngine,
        Request,
        Response,
        JSONResponse,
        HTMLResponse,
        Route,
        WebSocketRoute,
        WebSocket,
        Headers,
        QueryParams,
        UploadFile,
        TestClient,
    )
except ImportError as e:
    # Fallback for development
    import warnings
    warnings.warn(f"Could not import Rust extension: {e}. Please run 'maturin develop' to build the extension.")
    
    # Define stub classes for development
    class TachyonEngine:
        pass
    
    class Request:
        pass
    
    class Response:
        pass
    
    class JSONResponse:
        pass
    
    class HTMLResponse:
        pass
    
    class Route:
        pass
    
    class WebSocketRoute:
        pass
    
    class WebSocket:
        pass
    
    class Headers:
        pass
    
    class QueryParams:
        pass
    
    class UploadFile:
        pass
    
    class TestClient:
        pass

__all__ = [
    "TachyonEngine",
    "Request",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "Route",
    "WebSocketRoute",
    "WebSocket",
    "Headers",
    "QueryParams",
    "UploadFile",
    "TestClient",
]

__version__ = "0.1.0"
