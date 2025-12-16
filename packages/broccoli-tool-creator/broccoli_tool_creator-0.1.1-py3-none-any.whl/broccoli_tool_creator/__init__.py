from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

# Expose Config
from .config import ToolCreatorConfig
from .api import router as devtools_router
from .service import ToolAutomationService

def setup_tool_creator(app: FastAPI, config: ToolCreatorConfig):
    """
    Initialize the Broccoli Tool Creator on the FastAPI application.
    
    1. Stores config in app.state for the service dependency.
    2. Registers the /api/v1/dev-tools router.
    3. Overrides /docs to inject the 'Create Tool' button script.
    4. Initializes the DB service to ensure tables exist.
    """
    
    # Store config
    app.state.tool_creator_config = config
    
    # Initialize Service to ensure DB tables are created
    try:
        ToolAutomationService(config)
    except Exception:
        # Log but don't prevent app startup if DB is optional/failing
        # (Though config says we mask errors in _init_db anyway)
        pass
    
    # Register Router
    # We mount it under /api/v1/dev-tools by default or let user control prefix?
    # For now, hardcode to match previous assumption
    app.include_router(devtools_router, prefix="/api/v1/dev-tools", tags=["Dev Tools"])
    
    # Override Swagger UI
    # Note: Requires app to be initialized with docs_url=None
    
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        html = get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )
        
        # Inject custom script
        # Inject custom script with improved UI logic
        custom_js = """
        <script>
        window.onload = async function() {
            // 1. Fetch existing tools map
            let toolsMap = {};
            try {
                const res = await fetch('/api/v1/dev-tools/check-tools');
                if (res.ok) {
                    toolsMap = await res.json();
                    console.log('Loaded existing tools:', Object.keys(toolsMap).length);
                }
            } catch (e) {
                console.error('Failed to load existing tools:', e);
            }

            // 2. Observer to inject buttons
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.addedNodes.length) {
                        document.querySelectorAll('.opblock').forEach((opblock) => {
                             if (opblock.dataset.toolButtonAdded) return;
                             
                             const summary = opblock.querySelector('.opblock-summary');
                             if (summary) {
                                 // Extract method and path
                                 const classes = opblock.className.split(' ');
                                 const methodClass = classes.find(c => c.startsWith('opblock-') && c !== 'opblock-summary');
                                 const method = methodClass ? methodClass.replace('opblock-', '') : 'post';
                                 const path = opblock.querySelector('.opblock-summary-path').getAttribute('data-path');
                                 
                                 // Check if tool exists
                                 const existingTool = toolsMap[path];
                                 
                                 // Container for buttons
                                 const btnContainer = document.createElement('div');
                                 btnContainer.style.display = 'inline-flex';
                                 btnContainer.style.marginLeft = 'auto'; // Right align? Or just margin
                                 btnContainer.style.gap = '10px';
                                 btnContainer.style.marginLeft = '20px';
                                 
                                 // --- Action Button (Create or Update) ---
                                 const btn = document.createElement('button');
                                 btn.className = 'btn';
                                 btn.style.color = 'white';
                                 btn.style.border = 'none';
                                 btn.style.padding = '5px 10px';
                                 btn.style.borderRadius = '4px';
                                 btn.style.cursor = 'pointer';

                                 if (existingTool) {
                                     btn.innerText = 'Update Tool';
                                     btn.style.backgroundColor = '#e6a23c'; // Warning/Orange
                                 } else {
                                     btn.innerText = 'Create Tool';
                                     btn.style.backgroundColor = '#49cc90'; // Success/Green
                                 }
                                 
                                 btn.onclick = async (e) => {
                                     e.stopPropagation();
                                     const action = existingTool ? 'UPDATE' : 'CREATE';
                                     if (confirm(`${action} tool for ${method.toUpperCase()} ${path}?`)) {
                                         const origText = btn.innerText;
                                         try {
                                             btn.innerText = existingTool ? 'Updating...' : 'Creating...';
                                             const res = await fetch('/api/v1/dev-tools/create-from-endpoint', {
                                                 method: 'POST',
                                                 headers: {'Content-Type': 'application/json'},
                                                 body: JSON.stringify({path: path, method: method})
                                             });
                                             const data = await res.json();
                                             
                                             if (res.ok) {
                                                 // Update UI Map
                                                 if (data.status === 'created' || data.status === 'updated') {
                                                      // Assuming success means we have a tool.
                                                      // We might need to refresh the map or just manually update it if we had the full object.
                                                      if (data.status === 'created') {
                                                          alert('Success: Tool Created!');
                                                          // Reload page to refresh state or update explicitly? 
                                                          // Simplest: Reload map or just change button style
                                                          location.reload(); 
                                                      } else {
                                                          alert('Success: New version of tool is created!');
                                                          btn.innerText = 'Updated';
                                                          setTimeout(() => btn.innerText = 'Update Tool', 2000);
                                                      }
                                                 } else {
                                                     alert('Success: ' + data.message);
                                                 }
                                             } else {
                                                 alert('Error: ' + (data.detail || 'Unknown error'));
                                                 btn.innerText = origText;
                                             }
                                         } catch (err) {
                                             alert('Network Error: ' + err);
                                             btn.innerText = origText;
                                         }
                                     }
                                 };
                                 btnContainer.appendChild(btn);

                                 // --- Go to Tool Button (if exists) ---
                                 if (existingTool && existingTool.tool_id) {
                                     const viewBtn = document.createElement('button');
                                     viewBtn.innerText = 'Go to Tools';
                                     viewBtn.className = 'btn';
                                     viewBtn.style.backgroundColor = '#007bff'; // Blue
                                     viewBtn.style.color = 'white';
                                     viewBtn.style.border = 'none';
                                     viewBtn.style.padding = '5px 10px';
                                     viewBtn.style.borderRadius = '4px';
                                     viewBtn.style.cursor = 'pointer';
                                     
                                     viewBtn.onclick = (e) => {
                                         e.stopPropagation();
                                         // Use authenticated redirect endpoint
                                         const authUrl = `/api/v1/dev-tools/view-tool/${existingTool.tool_id}`;
                                         window.open(authUrl, '_blank');
                                     };
                                     btnContainer.appendChild(viewBtn);
                                 }

                                 summary.appendChild(btnContainer);
                                 opblock.dataset.toolButtonAdded = 'true';
                             }
                        });
                    }
                });
            });
            
            observer.observe(document.body, { childList: true, subtree: true });
        };
        </script>
        """
        return HTMLResponse(html.body.decode().replace("</body>", custom_js + "</body>"))
