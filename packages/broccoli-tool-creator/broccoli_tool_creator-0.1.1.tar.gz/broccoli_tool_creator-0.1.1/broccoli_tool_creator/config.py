from typing import Optional
from pydantic import BaseModel, Field

class ToolCreatorConfig(BaseModel):
    """Configuration for the Broccoli Tool Creator package"""
    
    # Broccoli API
    broccoli_api_url: str = Field(..., description="Base URL for the Broccoli backend API")
    
    # AWS Cognito Credentials
    cognito_client_id: str = Field(..., description="Cognito Client ID")
    cognito_pool_id: str = Field(..., description="Cognito User Pool ID (e.g., ap-south-1_XXXXX)")
    cognito_username: str = Field(..., description="Username for authentication (service account)")
    cognito_password: str = Field(..., description="Password for authentication")
    
    # Tool Metadata
    owner_id: str = Field(..., description="UUID of the tool owner (user/service)")
    schema_directory: str = Field(default="app/schemas", description="Directory containing Pydantic schemas (relative to run path)")
    tool_tracking_db_url: Optional[str] = Field(default=None, description="SQLAlchemy connection URL for external tool tracking DB")
    
    class Config:
        frozen = True
