"""
Type stubs for tachyon_engine
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union

class TachyonEngine:
    """Main ASGI application"""
    routes: List[Route]
    state: Dict[str, Any]
    
    def __init__(
        self,
        debug: bool = False,
        lifespan: Optional[Callable] = None,
    ) -> None: ...
    
    async def __call__(
        self,
        scope: Dict[str, Any],
        receive: Callable,
        send: Callable,
    ) -> None: ...
    
    def add_route(self, route: Route) -> None: ...
    
    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
    ) -> Callable: ...
    
    def add_middleware(self, middleware: Any) -> None: ...
    
    def build_middleware_stack(self, app: Any) -> Any: ...
    
    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None: ...

class Request:
    """HTTP Request object"""
    method: str
    url: str
    path: str
    headers: Headers
    query_params: QueryParams
    path_params: Dict[str, str]
    state: Dict[str, Any]
    cookies: Dict[str, str]
    
    def body(self) -> bytes: ...
    def json(self) -> Any: ...
    def form(self) -> Dict[str, Any]: ...
    def cookie(self, name: str) -> Optional[str]: ...
    def set_state(self, key: str, value: Any) -> None: ...

class Response:
    """HTTP Response"""
    status_code: int
    media_type: Optional[str]
    
    def __init__(
        self,
        content: Optional[bytes] = None,
        status_code: int = 200,
        headers: Optional[Headers] = None,
        media_type: Optional[str] = None,
    ) -> None: ...
    
    @property
    def body(self) -> bytes: ...
    
    @property
    def headers(self) -> Headers: ...
    
    def set_header(self, key: str, value: str) -> None: ...
    
    def set_cookie(
        self,
        key: str,
        value: str,
        max_age: Optional[int] = None,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        secure: Optional[bool] = None,
        httponly: Optional[bool] = None,
        samesite: Optional[str] = None,
    ) -> None: ...

class JSONResponse(Response):
    """JSON Response"""
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Headers] = None,
    ) -> None: ...

class HTMLResponse(Response):
    """HTML Response"""
    def __init__(
        self,
        content: str,
        status_code: int = 200,
        headers: Optional[Headers] = None,
    ) -> None: ...

class Route:
    """HTTP Route"""
    path: str
    endpoint: Callable
    methods: List[str]
    name: Optional[str]
    
    def __init__(
        self,
        path: str,
        endpoint: Callable,
        methods: List[str] = ["GET"],
        name: Optional[str] = None,
    ) -> None: ...

class WebSocketRoute:
    """WebSocket Route"""
    path: str
    endpoint: Callable
    name: Optional[str]
    
    def __init__(
        self,
        path: str,
        endpoint: Callable,
        name: Optional[str] = None,
    ) -> None: ...

class WebSocket:
    """WebSocket connection"""
    path: str
    query_params: QueryParams
    path_params: Dict[str, str]
    
    async def accept(self) -> None: ...
    async def send_text(self, data: str) -> None: ...
    async def send_json(self, data: Any) -> None: ...
    async def send_bytes(self, data: bytes) -> None: ...
    async def receive_text(self) -> str: ...
    async def receive_json(self) -> Any: ...
    async def receive_bytes(self) -> bytes: ...
    async def close(self, code: int = 1000) -> None: ...

class Headers:
    """HTTP Headers"""
    def __init__(self) -> None: ...
    def get(self, key: str) -> Optional[str]: ...
    def set(self, key: str, value: str) -> None: ...
    def contains(self, key: str) -> bool: ...
    def items(self) -> Dict[str, str]: ...
    def raw(self) -> List[Tuple[str, str]]: ...

class QueryParams:
    """Query parameters"""
    def __init__(self) -> None: ...
    def get(self, key: str) -> Optional[str]: ...
    def get_list(self, key: str) -> List[str]: ...
    def items(self) -> Dict[str, Union[str, List[str]]]: ...
    def contains(self, key: str) -> bool: ...

class UploadFile:
    """Uploaded file"""
    filename: str
    content_type: Optional[str]
    size: Optional[int]
    
    def __init__(
        self,
        filename: str,
        content_type: Optional[str] = None,
        content: bytes = b"",
    ) -> None: ...
    
    def read(self) -> bytes: ...
    def read_bytes(self, n: int) -> bytes: ...
    def seek(self, position: int) -> None: ...
    def close(self) -> None: ...
    def save(self, path: str) -> None: ...

class TestClient:
    """Test client for ASGI applications"""
    def __init__(
        self,
        app: TachyonEngine,
        base_url: str = "http://testserver",
    ) -> None: ...
    
    def get(
        self,
        url: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TestResponse: ...
    
    def post(
        self,
        url: str,
        json: Optional[Any] = None,
        data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TestResponse: ...
    
    def put(
        self,
        url: str,
        json: Optional[Any] = None,
        data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TestResponse: ...
    
    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> TestResponse: ...
    
    def patch(
        self,
        url: str,
        json: Optional[Any] = None,
        data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TestResponse: ...
    
    def __enter__(self) -> "TestClient": ...
    def __exit__(self, *args: Any) -> None: ...

class TestResponse:
    """Test response"""
    status_code: int
    headers: Dict[str, str]
    
    def content(self) -> bytes: ...
    def text(self) -> str: ...
    def json(self) -> Any: ...

