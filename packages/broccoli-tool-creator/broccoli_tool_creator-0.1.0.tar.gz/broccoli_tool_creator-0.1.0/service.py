"""
Automated Tool Creation Service for Broccoli Backend
"""

import ast
import json
import logging
import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import sqlite3
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy import create_engine, text



from .auth import CognitoSRPAuth
from .config import ToolCreatorConfig

logger = logging.getLogger(__name__)

class ToolAutomationService:
    """Automates the creation of tools from FastAPI endpoints"""

    def __init__(self, config: ToolCreatorConfig):
        self.config = config
        self.access_token = None
        self.id_token = None

        # Initialize Data Directory and DB Engine
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Determine DB URL
        if config.tool_tracking_db_url:
            self.db_url = config.tool_tracking_db_url
            logger.info("Using external DB for tool tracking")
        else:
            self.db_url = f"sqlite:///{self.data_dir / 'tools.db'}"
            logger.info("Using local SQLite for tool tracking")
            
        self.engine = create_engine(self.db_url)
        self._init_db()

        # Initialize Cognito auth
        self.cognito_auth = CognitoSRPAuth(
            client_id=config.cognito_client_id,
            username=config.cognito_username,
            password=config.cognito_password,
            pool_id=config.cognito_pool_id,
        )

    def _init_db(self):
        """Initialize the database for tracking tools"""
        print("\n[DEBUG] Initializing Tool Tracking DB...")
        # Mask password for logging
        safe_url = str(self.db_url)
        if ":" in safe_url and "@" in safe_url:
             try:
                part1 = safe_url.split("@")[1]
                print(f"[DEBUG] DB URL Host: {part1}")
             except Exception:
                pass
        
        try:
            with self.engine.connect() as conn:
                print("[DEBUG] Connected to DB. Checking/Creating table...")
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS created_tools (
                        function_name VARCHAR(255) PRIMARY KEY,
                        tool_id VARCHAR(255) NOT NULL,
                        tool_name VARCHAR(255) NOT NULL,
                        endpoint_url TEXT,
                        created_at TIMESTAMP,
                        last_updated TIMESTAMP
                    )
                '''))
                conn.commit()
                print("[DEBUG] Table check/creation complete.")
        except Exception as e:
            print(f"[ERROR] Failed to initialize tool database: {e}")
            logger.error(f"Failed to initialize tool database: {e}")


    def authenticate(self) -> bool:
        """Authenticate using AWS Cognito SRP and get tokens"""
        print("\n" + "=" * 60)
        print("AUTHENTICATING WITH AWS COGNITO")
        print("=" * 60)

        try:
            tokens = self.cognito_auth.authenticate()
            if tokens:
                self.access_token = tokens["access_token"]
                self.id_token = tokens["id_token"]
                print("[+] Authentication successful!")
                return True
            else:
                print("[-] Authentication failed")
                return False
        except Exception as e:
            print(f"[-] Authentication error: {e}")
            logger.error(f"Authentication error: {e}")
            return False

    def get_api_headers(self) -> Dict[str, str]:
        """Get headers for API calls to Broccoli backend"""
        return {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {self.id_token}",
            "content-type": "application/json",
            "origin": "https://dev2-broccoli.dailoqa.com",
            "referer": "https://dev2-broccoli.dailoqa.com/studio/tools/add",
            "x-user-email": self.cognito_auth.username,
            "x-user-id": self.config.owner_id,
        }

    def extract_endpoint_metadata(
        self, router_file_path: str, endpoint_path: Optional[str] = None, function_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from FastAPI endpoint using AST parsing
        
        Args:
            router_file_path: Path to the router file
            endpoint_path: Endpoint path (e.g., /initiate) - optional if function_name provided
            function_name: Name of the endpoint function - optional if endpoint_path provided
            
        Returns:
            Dictionary containing endpoint metadata
        """
        target_str = f"function '{function_name}'" if function_name else f"path '{endpoint_path}'"
        print(f"\n[*] Extracting metadata from {router_file_path} for {target_str}")

        try:
            with open(router_file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # Parse the source code
            tree = ast.parse(source_code)
            
            # Find the endpoint function - iterate through module body directly
            found_endpoints = []
            for node in tree.body:
                # Check if it's a function definition (sync or async)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Match by function name if provided
                    if function_name and node.name == function_name:
                        print(f"[+] Found endpoint by name: {node.name}")
                        # We still need the decorator to get method/path info
                        for decorator in node.decorator_list:
                             if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                                 if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == "router":
                                     # Found the router decorator
                                     return self._extract_function_metadata(node, decorator, source_code)
                    
                    # Look for @router decorators if matching by path
                    if not function_name and endpoint_path:
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Call):
                                if isinstance(decorator.func, ast.Attribute):
                                    if isinstance(decorator.func.value, ast.Name) and decorator.func.value.id == "router":
                                        func_attr = decorator.func.attr
                                        
                                        if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                            path = decorator.args[0].value
                                            found_endpoints.append(f"{func_attr.upper()} {path} -> {node.name}")
                                            
                                            if path == endpoint_path:
                                                print(f"[+] Found endpoint: {node.name}")
                                                return self._extract_function_metadata(node, decorator, source_code)

            if not function_name:
                print(f"[DEBUG] Found {len(found_endpoints)} endpoints in file:")
                for ep in found_endpoints:
                    print(f"  - {ep}")
                    
            print(f"[-] Could not find endpoint {target_str}")
            return None

        except Exception as e:
            print(f"[-] Error parsing file: {e}")
            # import traceback
            # traceback.print_exc()
            logger.error(f"Error parsing file: {e}", exc_info=True)
            return None

    def _extract_function_metadata(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef, decorator: ast.Call, source_code: str
    ) -> Dict[str, Any]:
        """Extract metadata from function AST node"""

        # Extract summary, response_model, and responses from decorator keywords
        summary = ""
        response_model_name = None
        http_method = "POST"
        responses_dict = {}
        
        for keyword in decorator.keywords:
            if keyword.arg == "summary" and isinstance(keyword.value, ast.Constant):
                summary = keyword.value.value
            elif keyword.arg == "response_model":
                # Extract response model name
                if isinstance(keyword.value, ast.Attribute):
                    response_model_name = keyword.value.attr
                elif isinstance(keyword.value, ast.Name):
                    response_model_name = keyword.value.id
                elif isinstance(keyword.value, ast.Subscript):
                    # Handle list[Model] or List[Model]
                    if isinstance(keyword.value.slice, ast.Name):
                        response_model_name = keyword.value.slice.id
                    elif isinstance(keyword.value.slice, ast.Attribute):
                         response_model_name = keyword.value.slice.attr

            elif keyword.arg == "responses" and isinstance(keyword.value, ast.Dict):
                # Extract response examples from dict
                for i, key in enumerate(keyword.value.keys):
                    if isinstance(key, ast.Constant) and isinstance(key.value, int):
                        status_code = key.value
                        val = keyword.value.values[i]
                        
                        if isinstance(val, ast.Dict):
                            try:
                                # Look for "content" -> "application/json"
                                for j, k in enumerate(val.keys):
                                    if isinstance(k, ast.Constant) and k.value == "content":
                                        content_dict = val.values[j]
                                        if isinstance(content_dict, ast.Dict):
                                            for l, m in enumerate(content_dict.keys):
                                                if isinstance(m, ast.Constant) and "json" in m.value:
                                                    json_dict = content_dict.values[l]
                                                    if isinstance(json_dict, ast.Dict):
                                                        # Check for "example" (singular)
                                                        for n, o in enumerate(json_dict.keys):
                                                            if isinstance(o, ast.Constant) and o.value == "example":
                                                                example_node = json_dict.values[n]
                                                                # Extract single example
                                                                responses_dict[status_code] = self._ast_to_python(example_node)
                                                            
                                                            # Check for "examples" (plural)
                                                            elif isinstance(o, ast.Constant) and o.value == "examples":
                                                                examples_node = json_dict.values[n]
                                                                if isinstance(examples_node, ast.Dict):
                                                                    # Take the first example value found
                                                                    if examples_node.values:
                                                                        first_ex_val = examples_node.values[0]
                                                                        if isinstance(first_ex_val, ast.Dict):
                                                                             # Look for "value" key inside example definition
                                                                             for p, q in enumerate(first_ex_val.keys):
                                                                                 if isinstance(q, ast.Constant) and q.value == "value":
                                                                                     responses_dict[status_code] = self._ast_to_python(first_ex_val.values[p])
                                                                                     break
                            except Exception:
                                pass

        # Extract HTTP method from decorator
        if hasattr(decorator.func, "attr"):
            http_method = decorator.func.attr.upper()

        # Extract docstring
        docstring = ast.get_docstring(func_node) or ""
        
        # Parse docstring for parameter descriptions
        docstring_params = self._parse_docstring_parameters(docstring)

        # Extract Form/File parameters from function signature
        form_file_params = self._extract_form_file_parameters(func_node)

        # Extract function arguments (request body schema) - for JSON endpoints
        request_schema_name = None
        for arg in func_node.args.args:
            if arg.arg not in ["db", "self", "request", "response"]:  # Skip dependencies
                if arg.annotation:
                    # Extract schema name from annotation
                    if isinstance(arg.annotation, ast.Attribute):
                        request_schema_name = arg.annotation.attr
                    elif isinstance(arg.annotation, ast.Name):
                        request_schema_name = arg.annotation.id
                    break  # Take first non-dependency parameter

        return {
            "function_name": func_node.name,
            "http_method": http_method,
            "summary": summary,
            "docstring": docstring,
            "docstring_params": docstring_params,
            "form_file_params": form_file_params,  # NEW: Form/File parameters
            "request_schema": request_schema_name,
            "response_schema": response_model_name,
            "responses": responses_dict,
        }
    
    def _extract_form_file_parameters(self, func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[Dict[str, Any]]:
        """Extract Form and File parameters from function signature"""
        params = []
        
        for arg in func_node.args.args:
            # Skip common dependencies
            if arg.arg in ["db", "self", "request", "response"]:
                continue
            
            # Check if arg has a default value that's Form() or File()
            if func_node.args.defaults:
                # Map args to their defaults
                num_args = len(func_node.args.args)
                num_defaults = len(func_node.args.defaults)
                default_offset = num_args - num_defaults
                
                arg_index = func_node.args.args.index(arg)
                if arg_index >= default_offset:
                    default_index = arg_index - default_offset
                    default_val = func_node.args.defaults[default_index]
                    
                    # Check if it's a Form() or File() call
                    if isinstance(default_val, ast.Call):
                        func_name = None
                        if isinstance(default_val.func, ast.Name):
                            func_name = default_val.func.id
                        
                        if func_name in ["Form", "File"]:
                            # Extract parameter metadata
                            param_info = {
                                "name": arg.arg,
                                "type": func_name.lower(),  # 'form' or 'file'
                                "required": False,
                                "description": "",
                                "examples": []
                            }
                            
                            # Check if first arg is ... (required)
                            if default_val.args and isinstance(default_val.args[0], ast.Constant):
                                if default_val.args[0].value == Ellipsis:
                                    param_info["required"] = True
                            
                            # Extract keyword arguments from Form/File call
                            for kw in default_val.keywords:
                                if kw.arg == "description" and isinstance(kw.value, ast.Constant):
                                    param_info["description"] = kw.value.value
                                elif kw.arg == "examples" and isinstance(kw.value, ast.List):
                                    param_info["examples"] = [
                                        el.value for el in kw.value.elts 
                                        if isinstance(el, ast.Constant)
                                    ]
                            
                            # Determine parameter type from annotation
                            if arg.annotation:
                                type_str = ast.unparse(arg.annotation)
                                
                                # Map to tool-friendly types
                                if "UploadFile" in type_str or func_name == "File":
                                    param_info["param_type"] = "file"
                                elif "int" in type_str:
                                    param_info["param_type"] = "integer"
                                elif "str" in type_str:
                                    param_info["param_type"] = "string"
                                elif "bool" in type_str:
                                    param_info["param_type"] = "boolean"
                                else:
                                    param_info["param_type"] = "string"
                            else:
                                param_info["param_type"] = "string"
                            
                            params.append(param_info)
        
        return params

    
    def _parse_docstring_parameters(self, docstring: str) -> Dict[str, str]:
        """Parse parameter descriptions from docstring"""
        params = {}
        if not docstring:
            return params
        
        # Look for lines with - **param_name**: description
        try:
           pattern = r'-\s+\*\*([^*]+)\*\*:\s*(.+)'
           for match in re.finditer(pattern, docstring):
               param_name = match.group(1).strip()
               description = match.group(2).strip()
               params[param_name] = description
        except Exception:
            pass
        
        return params


    def create_tool_payload(
        self, endpoint_url: str, metadata: Dict[str, Any], tool_name: str
    ) -> Dict[str, Any]:
        """
        Create the payload for API 1 (tool creation)

        Args:
            endpoint_url: Full URL to the endpoint
            metadata: Extracted metadata from endpoint
            tool_name: Name for the tool

        Returns:
            Payload dictionary for tool creation
        """
        # Build parameters from Form/File params (for file upload endpoints) or docstring params (for JSON endpoints)
        parameters_list = []
        form_file_params = metadata.get("form_file_params", [])
        doc_params = metadata.get("docstring_params", {})
        
        # Prioritize Form/File parameters if they exist (file upload endpoints)
        if form_file_params:
            print(f"[DEBUG] Using Form/File parameters: {len(form_file_params)} params")
            for param in form_file_params:
                param_type = param.get("param_type", "string")
                
                # Get example from the param
                example = ""
                if param.get("examples"):
                    example = str(param["examples"][0])
                elif param_type == "integer":
                    example = "1234"
                elif param_type == "file":
                    example = "@document.pdf"
                else:
                    example = "value"
                
                parameters_list.append({
                    "key": param["name"],
                    "description": param["description"] or f"{param['name']} parameter",
                    "type": param_type,
                    "options": "",
                    "example": example,
                })
        elif doc_params:
            # Fallback to docstring parameters (JSON endpoints)
            print(f"[DEBUG] Using docstring parameters: {len(doc_params)} params")
            for param_name, param_desc in doc_params.items():
                # Determine type from description hints
                param_type = "string"  # Default
                example = ""
                
                if "phone" in param_name.lower() or "number" in param_desc.lower():
                    param_type = "string"
                    example = "1234567890"
                elif "id" in param_name.lower():
                    param_type = "integer"
                    example = "1"
                elif "date" in param_name.lower():
                    param_type = "date"
                    example = "2024-01-01"
                elif "role" in param_name.lower():
                    param_type = "string"
                    example = "user"
                
                # Truncate description if too long
                description = param_desc
                if len(description) > 500:
                    description = description[:500] + "..."

                parameters_list.append({
                    "key": param_name,
                    "description": description,
                    "type": param_type,
                    "options": "",
                    "example": example,
                })
        else:
            # Fallback to generic parameter  
            request_schema = metadata.get("request_schema", "")
            description = f"{metadata.get('summary', 'Request body')} (Schema: {request_schema})"
            if len(description) > 500:
                description = description[:500] + "..."
                
            parameters_list.append({
                "key": "request_body",
                "description": description,
                "type": "json",
                "options": "",
                "example": "{}",
            })



        # Build detailed output description from response schema
        response_schema = metadata.get("response_schema", "")
        responses_dict = metadata.get("responses", {})
        
        # Default fallback if no schema found
        output_description = json.dumps(responses_dict) or json.dumps(response_schema)#"Structure of the API response" 
        output_example = '{"status": 200, "data": {}}'
        
        # Check for explicit examples in responses dict (from decorator)
        example_data = None
        if responses_dict:
            # Prefer success codes
            for code in [200, 201]:
                if code in responses_dict:
                    example_data = responses_dict[code]
                    output_example = json.dumps(example_data, indent=2)
                    break
        
        if response_schema:
            # Try to parse response schema for detailed output
            schema_fields = self._extract_pydantic_schema_fields(response_schema)
            
            if schema_fields:
                # Build detailed description with field information
                field_descriptions = []
                example_output = example_data if example_data else {}
                
                for field in schema_fields:
                    field_name = field.get('name', '')
                    field_desc = field.get('description', '')
                    field_type = field.get('type', 'string')
                    
                    if field_desc:
                        field_descriptions.append(f"{field_name} ({field_type}): {field_desc}")
                    else:
                        field_descriptions.append(f"{field_name} ({field_type})")
                    
                    # Build example output if not provided by decorator
                    if not example_data:
                        if field.get('example'):
                            example_output[field_name] = field.get('example')
                        elif field_type == 'integer':
                            example_output[field_name] = 1234
                        elif field_type == 'boolean':
                            example_output[field_name] = True
                        elif field_type == 'array':
                            example_output[field_name] = []
                        else:
                            example_output[field_name] = "value"
                
                if field_descriptions:
                    # Create a readable summary of fields (max 5-7 lines)
                    desc_lines = [f"JSON response matching {response_schema} schema containing:"]
                    for desc in field_descriptions[:7]:
                        desc_lines.append(f"- {desc}")
                    if len(field_descriptions) > 7:
                        desc_lines.append(f"... and {len(field_descriptions) - 7} more fields")
                    
                    if example_data:
                        desc_lines.append("\nExample Response:")
                        desc_lines.append(json.dumps(example_data, indent=2))

                    output_description = "\\n".join(desc_lines)
                    
                    if not example_data:
                        output_example = json.dumps(example_output, indent=2)
            else:
                output_description = f"JSON response validation against {response_schema} schema"
                if example_data:
                    output_description += f"\n\nExample:\n{json.dumps(example_data, indent=2)}"
        else:
             # Fallback if no schema is defined at all
             if example_data:
                 output_description = f"Returns JSON object. Example:\n{json.dumps(example_data, indent=2)}"
             else:
                 output_description = "Consult endpoint documentation for response structure"

        # Enforce max length for output_description (API limit is 2000 characters)
        if len(output_description) > 1900:
            print(f"[WARN] output_description tool long ({len(output_description)} chars). Truncating.")
            output_description = output_description[:1900] + "... (truncated)"
        
        payload = {
            "toolId": "",
            "toolName": tool_name,
            "toolDescription": metadata.get("summary", ""),
            "toolRemarks": f"Auto-generated from {metadata.get('function_name', 'endpoint')}",
            "toolUrlEndpoint": endpoint_url,
            "toolAuthentication": "",
            "toolParameters": {"parameters": parameters_list, "testMode": True},
            "toolOutput": {
                "parameters": {
                    "output": {
                        "description": output_description,
                        "type": "json",
                        "example": output_example,
                    }
                }
            },
            "toolAnnotation": "",  # Will be filled by API 2
            "ownerId": self.config.owner_id,
            "toolTimeout": "90",
            "toolTags": ["auto-generated"],
            "tags": [],
            "isCore": False,
            "isAuthPresent": False,
            "accessControl": {
                "viewAccessType": "Public",
                "viewAllowedUsers": [],
                "editAccessType": "Public",
                "editAllowedUsers": [],
            },
            "toolParent": "null", # Keep as "null" string as per tool_automation 
            # WAIT: In previous validation I changed None to "" for toolParent. 
            # In user's tool_automation.py they set: "toolParent": "null".
            # This is interesting. "null" string might be what broccoli expects if not present?
            # Or maybe just empty string. Since I verified "" works, I might stick to that, 
            # BUT the user's manual file says "null". I will try "null".
            "versions": [{"version": "1", "toolId": "", "isDefault": True}],
            "default": True,
            "toolVersion": "1",
        }

        # Override toolParent to match my successful fix if needed, 
        # but let's trust the user's manual file if they say it was "working".
        # Actually, user said logs failed in 1060 with 500 error on toolParent null check.
        # My success fix was empty string "". 
        # I will use empty string "" based on my successful verification step earlier.
        payload["toolParent"] = ""

        return payload

    def _extract_pydantic_schema_fields(self, schema_name: str) -> List[Dict[str, Any]]:
        """Extract fields from a Pydantic schema definition by searching configured schemas directory"""
        fields = []
        schemas_dir = Path(self.config.schema_directory)
        
        if not schemas_dir.exists():
            return fields
            
        print(f"[DEBUG] Searching for schema {schema_name} in {schemas_dir}...")
        
        for schema_file in schemas_dir.glob("*.py"):
            try:
                with open(schema_file, "r", encoding="utf-8") as f:
                    source_code = f.read()
                    
                tree = ast.parse(source_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == schema_name:
                        print(f"[DEBUG] Found schema in {schema_file.name}")
                        
                        # Extract fields
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                field_name = item.target.id
                                field_info = {
                                    "name": field_name,
                                    "type": "string",
                                    "description": ""
                                }
                                
                                # Try to get type
                                if item.annotation:
                                    field_info["type"] = self._ast_node_to_string(item.annotation)
                                
                                # Try to get description and examples from Field()
                                if item.value and isinstance(item.value, ast.Call):
                                    func_name = ""
                                    if isinstance(item.value.func, ast.Name):
                                        func_name = item.value.func.id
                                        
                                    if func_name == "Field":
                                        for kw in item.value.keywords:
                                            if kw.arg == "description" and isinstance(kw.value, ast.Constant):
                                                field_info["description"] = kw.value.value
                                            elif kw.arg == "examples" and isinstance(kw.value, ast.List):
                                                if kw.value.elts and isinstance(kw.value.elts[0], ast.Constant):
                                                    field_info["example"] = kw.value.elts[0].value
                                
                                fields.append(field_info)
                        return fields
            except Exception as e:
                continue
                
        return fields

    def _ast_node_to_string(self, node: ast.AST) -> str:
        """Convert AST annotation node to string"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            value = self._ast_node_to_string(node.value)
            slice_val = self._ast_node_to_string(node.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            return node.attr
        return "any"

    def _ast_to_python(self, node: ast.AST) -> Any:
        """Convert AST node to Python object"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Dict):
            result = {}
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant):
                    result[k.value] = self._ast_to_python(v)
            return result
        elif isinstance(node, ast.List):
            return [self._ast_to_python(elt) for elt in node.elts]
        elif isinstance(node, ast.Name):
            # Special handling for constants usually found in code like "True", "False", "None"
            if node.id == "True":
                return True
            elif node.id == "False":
                return False
            elif node.id == "None":
                return None
            return node.id
        return None

    def call_api1_create_tool(self, payload: Dict[str, Any]) -> Optional[str]:
        """
        Call API 1 to create a tool

        Args:
            payload: Tool creation payload

        Returns:
            Tool ID if successful, None otherwise
        """
        print("\n" + "=" * 60)
        print("API 1: CREATING TOOL")
        print("=" * 60)

        url = f"{self.config.broccoli_api_url}/api/tools"

        try:
            response = requests.post(url, headers=self.get_api_headers(), json=payload)

            if response.status_code in [200, 201]:  # Accept both OK and Created
                result = response.json()
                tool_id = result.get("toolId")
                print("[+] Tool created successfully!")
                print(f"  Tool ID: {tool_id}")
                print(f"  Tool Name: {result.get('toolName')}")
                return tool_id
            else:
                print(f"[-] Tool creation failed: {response.status_code}")
                print(f"  Response: {response.text}")
                logger.error(f"Tool creation failed details: {response.text}")
                return None

        except Exception as e:
            print(f"[-] Error calling API 1: {e}")
            logger.error(f"Error calling API 1: {e}", exc_info=True)
            return None

    def call_api_update_tool(self, tool_id: str, payload: Dict[str, Any]) -> bool:
        """Video update for an existing tool"""
        print("\n" + "=" * 60)
        print(f"UPDATING EXISTING TOOL: {tool_id}")
        print("=" * 60)
        
        # Ensure payload has the ID
        payload["toolId"] = tool_id
        
        # Broccoli update usually implies PUT to /api/tools or /api/tools/{id}
        # Based on typical REST patterns and the fact creation is POST /api/tools
        url = f"{self.config.broccoli_api_url}/api/tools/{tool_id}"
        
        try:
            # Try PUT first
            response = requests.put(url, headers=self.get_api_headers(), json=payload)
            
            if response.status_code in [200, 204]:
                print(f"[+] Tool updated successfully!")
                return True
            elif response.status_code == 400:
                # Handle Version Mismatch (Optimistic Locking)
                # Error format: "tool version is not matching to the tables record, it should be: 2"
                resp_text = response.text
                if "tool version" in resp_text and "should be" in resp_text:
                    import re
                    match = re.search(r"should be:\s*(\d+)", resp_text)
                    if match:
                        correct_version = match.group(1)
                        print(f"[!] Version mismatch detected. Retrying with version: {correct_version}")
                        
                        payload["toolVersion"] = correct_version
                        retry_response = requests.put(url, headers=self.get_api_headers(), json=payload)
                        
                        if retry_response.status_code in [200, 204]:
                            print(f"[+] Tool updated successfully (after retry)!")
                            return True
                        else:
                            print(f"[-] Retry failed: {retry_response.status_code}")
                            print(f"  Response: {retry_response.text}")
                            return False

                print(f"[-] Tool update failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
            else:
                print(f"[-] Tool update failed: {response.status_code}")
                print(f"  Response: {response.text}")
                
                # Fallback: Maybe POST to /api/tools with ID? (Unlikely but possible)
                if response.status_code == 404: 
                    print("  [DEBUG] 404 on PUT, resource might be missing or URL differs.")
                return False
                
        except Exception as e:
             print(f"[-] Error calling Update API: {e}")
             return False


    def call_api2_generate_annotation(
        self, tool_payload: Dict[str, Any]
    ) -> Optional[str]:
        """
        Call API 2 to generate AI annotation

        Args:
            tool_payload: Tool payload (similar to API 1)

        Returns:
            Generated annotation if successful, None otherwise
        """
        print("\n" + "=" * 60)
        print("API 2: GENERATING AI ANNOTATION")
        print("=" * 60)

        url = f"{self.config.broccoli_api_url}/api/annotation"

        # Create annotation payload (subset of tool payload)
        annotation_payload = {
            "toolName": tool_payload["toolName"],
            "toolDescription": tool_payload["toolDescription"],
            "toolUrlEndpoint": tool_payload["toolUrlEndpoint"],
            "toolParameters": tool_payload["toolParameters"],
            "toolOutput": tool_payload["toolOutput"],
        }

        try:
            response = requests.post(
                url, headers=self.get_api_headers(), json=annotation_payload
            )

            if response.status_code == 200:
                result = response.json()
                annotation = result.get("aiAnnotation", "")
                print("[+] Annotation generated successfully!")
                return annotation
            else:
                print(f"[-] Annotation generation failed: {response.status_code}")
                # Don't fail the whole process just for annotation
                return None

        except Exception as e:
            print(f"[-] Error calling API 2: {e}")
            return None

    def call_api_find_tool(self, tool_name: str) -> Optional[str]:
        """
        Check if tool exists remotely (Search & Adopt Strategy).
        Currently a placeholder as user doesn't have the API yet.
        """
        print(f"\n[DEBUG] Searching valid remote tool: '{tool_name}'")
        # Placeholder: Return None to simulate "Not Found" for now,
        # OR implement a basic GET /api/tools if we dared.
        # User instruction: "leave place holder for api call"
        return None

    def create_tool_from_endpoint(
        self,
        router_file: str,
        endpoint_path: Optional[str] = None,
        endpoint_url: str = "",
        tool_name: Optional[str] = None,
        function_name: Optional[str] = None,
    ) -> bool:
        """
        Main automation flow: Create a tool from a FastAPI endpoint

        Args:
            router_file: Path to router file
            endpoint_path: Endpoint path (e.g., /initiate)
            endpoint_url: Full URL to the endpoint
            tool_name: Optional custom tool name
            function_name: Optional name of the function to look for
        """
        print("\n" + "=" * 80)
        print("AUTOMATED TOOL CREATION")
        print("=" * 80)
        print(f"Router File: {router_file}")
        print(f"Function: {function_name}")
        print(f"Endpoint URL: {endpoint_url}")
        print("=" * 80)

        # Step 1: Authenticate
        if not self.authenticate():
            return False

        # Step 2: Extract endpoint metadata
        metadata = self.extract_endpoint_metadata(router_file, endpoint_path, function_name)
        if not metadata:
            return False

        print("\n[+] Metadata extracted:")
        print(f"  Function: {metadata.get('function_name')}")
        print(f"  Method: {metadata.get('http_method')}")
        print(f"  Summary: {metadata.get('summary')}")

        # Step 3: Determine Tool Name and Check for Update
        metadata_func_name = metadata.get('function_name', 'tool')
        
        # Check local DB for existing tool
        existing_tool = self._get_tool_from_db(metadata_func_name)
        
        if tool_name:
             # If user provided a specific name, use it (but we might drift from stored function binding)
             pass
        else:
             # Use stable name (no date) for persistence matching
             # However, if we didn't find it in DB, we should probably keep it clean
             tool_name = metadata_func_name
        
        # Step 4: Create tool payload
        tool_payload = self.create_tool_payload(endpoint_url, metadata, tool_name)
        
        # Step 5: Generate annotation first (API 2)
        annotation = self.call_api2_generate_annotation(tool_payload)
        if annotation:
            # Enforce max length (API limit is 2000 chars)
            if len(annotation) > 1900:
                print(f"[WARN] Generated annotation too long ({len(annotation)} chars). Truncating.")
                annotation = annotation[:1900] + "..."
            
            tool_payload["toolAnnotation"] = annotation
            # print(f"[DEBUG] Final toolAnnotation length: {len(tool_payload['toolAnnotation'])}")

        # Step 6: Create or Update Tool
        tool_id = None
        
        if existing_tool:
            # Case A: Found locally -> UPDATE
            stored_tool_id, stored_tool_name = existing_tool
            print(f"[INFO] Found existing tool '{stored_tool_name}' (ID: {stored_tool_id}) in LOCAL DB.")
            
            tool_payload["toolId"] = stored_tool_id
            tool_payload["toolName"] = stored_tool_name 
            
            if self.call_api_update_tool(stored_tool_id, tool_payload):
                tool_id = stored_tool_id
                self._update_tool_db(metadata_func_name)
        else:
            # Case B: Not found locally -> Check Remote (Sync)
            print("[INFO] Not found in Local DB. Checking Remote...")
            remote_tool_id = self.call_api_find_tool(tool_name)
            
            if remote_tool_id:
                # Case B.1: Found remotely -> ADOPT & UPDATE
                print(f"[INFO] Found existing tool remotely (ID: {remote_tool_id}). Adopting...")
                
                # Save to local DB first
                self._save_tool_to_db(metadata_func_name, remote_tool_id, tool_name, endpoint_url)
                
                # Then Update
                tool_payload["toolId"] = remote_tool_id
                if self.call_api_update_tool(remote_tool_id, tool_payload):
                     tool_id = remote_tool_id
                     self._update_tool_db(metadata_func_name)
            else:
                # Case B.2: Not found remotely -> CREATE
                print("[INFO] Not found remotely. Creating new tool...")
                tool_id = self.call_api1_create_tool(tool_payload)
                if tool_id:
                    self._save_tool_to_db(metadata_func_name, tool_id, tool_name, endpoint_url)

        if tool_id:
            print("\n" + "=" * 80)
            print("[+] TOOL OPERATION SUCCESSFUL!")
            print("=" * 80)
            return {
                "success": True, 
                "status": "updated" if existing_tool or (remote_tool_id and not existing_tool) else "created",
                "tool_id": tool_id
            }
        return {"success": False, "status": "failed"}

    def _get_tool_from_db(self, function_name: str) -> Optional[Tuple[str, str]]:
        """Check if tool exists in DB"""
        try:
            print(f"[DEBUG] Checking DB for tool with function_name: '{function_name}'")
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT tool_id, tool_name FROM created_tools WHERE function_name = :function_name"),
                    {"function_name": function_name}
                )
                row = result.fetchone()
                if row:
                    print(f"[DEBUG] Found in DB: ID={row[0]}")
                    return (row[0], row[1])
                else:
                    print(f"[DEBUG] Not found in DB.")
                    return None
        except Exception as e:
            print(f"[ERROR] DB Read Error in _get_tool_from_db: {e}")
            logger.error(f"DB Read Error: {e}")
            return None


    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools from the local database.
        Returns a list of dicts with tool info (path, id, name).
        Used by the UI to determine which buttons to show.
        """
        tools = []
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT tool_id, tool_name, endpoint_url FROM created_tools"))
                for row in result:
                    # Parse path from endpoint_url
                    # e.g., http://localhost:8000/api/v1/leads/initiate -> /api/v1/leads/initiate
                    endpoint_url = row[2]
                    path = endpoint_url
                    if "://" in endpoint_url:
                        try:
                            # Split by third slash
                            parts = endpoint_url.split("/", 3)
                            if len(parts) > 3:
                                path = "/" + parts[3]
                        except Exception as e:
                            print(f"[WARN] Failed to parse path from {endpoint_url}: {e}")
                    
                    tool_data = {
                        "tool_id": row[0],
                        "tool_name": row[1],
                        "endpoint_url": endpoint_url,
                        "path": path,
                        "view_url": f"{self.config.broccoli_api_url}/studio/tools/view/{row[0]}"
                    }
                    tools.append(tool_data)
                    print(f"[DEBUG] Loaded tool: {row[1]} -> path={path}")
            
            print(f"[DEBUG] get_all_tools returning {len(tools)} tools")
            return tools
        except Exception as e:
            logger.error(f"Error fetching all tools: {e}")
            return []

    def _save_tool_to_db(self, function_name: str, tool_id: str, tool_name: str, endpoint_url: str):
        """Save new tool to DB"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO created_tools (function_name, tool_id, tool_name, endpoint_url, created_at, last_updated) VALUES (:function_name, :tool_id, :tool_name, :endpoint_url, :created_at, :last_updated)"),
                    {
                        "function_name": function_name,
                        "tool_id": tool_id,
                        "tool_name": tool_name,
                        "endpoint_url": endpoint_url,
                        "created_at": datetime.now(),
                        "last_updated": datetime.now()
                    }
                )
                conn.commit()
        except Exception as e:
            logger.error(f"DB Save Error: {e}")

    def _update_tool_db(self, function_name: str):
        """Update last_updated timestamp"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text("UPDATE created_tools SET last_updated = :last_updated WHERE function_name = :function_name"),
                    {
                        "last_updated": datetime.now(),
                        "function_name": function_name
                    }
                )
                conn.commit()
        except Exception as e:
            logger.error(f"DB Update Error: {e}")

