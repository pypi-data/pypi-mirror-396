import inspect
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel

# Import Service and Config from package (relative imports)
from .service import ToolAutomationService
from .config import ToolCreatorConfig

logger = logging.getLogger(__name__)

# Request Model
class ToolCreationRequest(BaseModel):
    path: str
    method: str = "POST"
    tool_name: Optional[str] = None

# Dependency to get service with pre-configured settings
def get_tool_service(request: Request) -> ToolAutomationService:
    if not hasattr(request.app.state, "tool_creator_config"):
         raise HTTPException(status_code=500, detail="Tool Creator not configured")
    # Retrieve config from app state
    config: ToolCreatorConfig = request.app.state.tool_creator_config
    return ToolAutomationService(config)

router = APIRouter()

@router.post("/create-from-endpoint")
async def create_tool_from_endpoint_api(
    request: Request, 
    body: ToolCreationRequest,
    service: ToolAutomationService = Depends(get_tool_service)
):
    """
    Trigger tool creation for a specific endpoint.
    Found by finding the matching route in the FastAPI app.
    """
    logger.info(f"Received tool creation request for {body.method} {body.path}")
    
    # Normalize path (ensure leading slash)
    target_path = body.path if body.path.startswith("/") else f"/{body.path}"
    target_method = body.method.upper()
    
    # 1. Find the route handler
    found_route = None
    for route in request.app.routes:
        # Check standard APIRoute
        if hasattr(route, "path") and hasattr(route, "methods"):
             if route.path == target_path and target_method in route.methods:
                 found_route = route
                 break
    
    if not found_route:
        # Generic match attempt (handling potential path formatting)
        for route in request.app.routes:
             if hasattr(route, "path_format") and route.path_format == target_path and target_method in route.methods:
                 found_route = route
                 break
                 
    if not found_route:
        logger.warning(f"Endpoint {target_method} {target_path} not found")
        raise HTTPException(status_code=404, detail=f"Endpoint {target_method} {target_path} not found in application routes")
        
    # 2. Get the source file of the handler
    handler = found_route.endpoint
    
    # Unwrap decorated functions (e.g., @opik.track) to get to the actual function
    while hasattr(handler, "__wrapped__"):
        handler = handler.__wrapped__
        
    source_file = None
    try:
        source_file = inspect.getsourcefile(handler)
        if not source_file:
             raise ValueError("Could not determine source file")
    except Exception as e:
        logger.error(f"Failed to locate source file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to locate source file: {str(e)}")

    logger.info(f"Found handler '{handler.__name__}' in {source_file}")

    # 3. Create tool
    try:
        # Determine accessible URL
        full_url = str(request.base_url).rstrip("/") + target_path
        
        result = service.create_tool_from_endpoint(
             router_file=source_file,
             endpoint_path=None, 
             endpoint_url=full_url,
             tool_name=body.tool_name,
             function_name=handler.__name__ 
        )
        
        if isinstance(result, dict) and result.get("success"):
             return {
                 "message": "Tool created successfully", 
                 "tool_name": body.tool_name or f"{handler.__name__}_{target_method}",
                 "status": result.get("status", "created"),
                 "tool_id": result.get("tool_id")
             }
        elif result is True: # Fallback for legacy bool return if any
             return {"message": "Tool created successfully", "tool_name": body.tool_name}
        else:
             raise HTTPException(status_code=500, detail="Tool creation failed (check server logs)")
             
    except Exception as e:
        logger.error(f"Error creating tool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check-tools")
async def check_existing_tools(
    request: Request,
    service: ToolAutomationService = Depends(get_tool_service)
):
    """
    Get list of all existing tools to support UI buttons.
    Returns: { "path": { "tool_id": "...", "status": "exists", "view_url": "..." } }
    """
    try:
        tools = service.get_all_tools()
        # Convert list to map for easier frontend lookup
        # Keying by path or function_name
        tools_map = {}
        for tool in tools:
            path = tool.get("path")
            if path:
                tools_map[path] = tool
        return tools_map
    except Exception as e:
        logger.error(f"Error checking tools: {e}")
        return {}

@router.get("/view-tool/{tool_id}")
async def view_tool_authenticated(
    tool_id: str,
    service: ToolAutomationService = Depends(get_tool_service)
):
    """
    Redirect to the proxy endpoint that will serve the Broccoli tool view with authentication.
    """
    from fastapi.responses import RedirectResponse
    # Redirect to the proxy endpoint
    return RedirectResponse(url=f"/api/v1/dev-tools/broccoli-proxy/studio/tools/view/{tool_id}")

@router.get("/broccoli-proxy/{path:path}")
async def broccoli_proxy(
    path: str,
    request: Request,
    service: ToolAutomationService = Depends(get_tool_service)
):
    """
    Proxy endpoint that forwards requests to Broccoli with authentication.
    This allows users to access Broccoli tools through the backend with automatic auth.
    """
    import httpx
    
    try:
        # Authenticate to get access token
        if not service.authenticate():
            raise HTTPException(status_code=500, detail="Authentication failed")
        
        access_token = service.access_token
        
        # Construct the target Broccoli URL
        broccoli_base = service.config.broccoli_api_url
        target_url = f"{broccoli_base}/{path}"
        
        # Get query parameters from the original request
        query_params = dict(request.query_params)
        
        # Prepare headers for the proxied request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": request.headers.get("accept", "*/*"),
            "Content-Type": request.headers.get("content-type", "application/json"),
        }
        
        # Forward the request to Broccoli
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            if request.method == "GET":
                response = await client.get(target_url, headers=headers, params=query_params)
            elif request.method == "POST":
                body = await request.body()
                response = await client.post(target_url, headers=headers, params=query_params, content=body)
            elif request.method == "PUT":
                body = await request.body()
                response = await client.put(target_url, headers=headers, params=query_params, content=body)
            elif request.method == "DELETE":
                response = await client.delete(target_url, headers=headers, params=query_params)
            else:
                raise HTTPException(status_code=405, detail=f"Method {request.method} not supported")
        
        # Return the response from Broccoli
        from fastapi.responses import Response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
        
    except httpx.HTTPError as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to connect to Broccoli: {str(e)}")
    except Exception as e:
        logger.error(f"Error in proxy: {e}")
        raise HTTPException(status_code=500, detail=str(e))
