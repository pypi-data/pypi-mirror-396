"""
Simple example application using Tachyon Engine
"""

from tachyon_engine import TachyonEngine, Route, Request, JSONResponse

# Create application
app = TachyonEngine(debug=True)


# Define route handlers
async def homepage(request: Request):
    """Homepage handler"""
    return JSONResponse({
        "message": "Welcome to Tachyon Engine!",
        "path": request.path,
        "method": request.method,
    })


async def hello_user(request: Request):
    """User greeting handler"""
    user_id = request.path_params.get("user_id")
    return JSONResponse({
        "message": f"Hello, user {user_id}!",
        "user_id": user_id,
    })


async def echo_json(request: Request):
    """Echo JSON body"""
    try:
        body = request.json()
        return JSONResponse({
            "echo": body,
            "status": "received",
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e),
        }, status_code=400)


# Add routes
app.add_route(Route("/", homepage, methods=["GET"]))
app.add_route(Route("/users/{user_id}", hello_user, methods=["GET"]))
app.add_route(Route("/echo", echo_json, methods=["POST"]))


if __name__ == "__main__":
    print("🚀 Starting Tachyon Engine example")
    print("   Routes:")
    for route in app.routes:
        print(f"   - {route.methods} {route.path}")
    print()
    
    # app.run(host="0.0.0.0", port=8000)
    print("Note: Server functionality coming soon!")
    print("      Current version demonstrates API compatibility with Starlette")

