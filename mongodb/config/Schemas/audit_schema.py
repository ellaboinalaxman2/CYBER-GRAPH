from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from ..models.audit_log import AuditAction

class AuditSchema(BaseModel):
    """Audit log schema for validation"""
    
    audit_id: str = Field(..., description="Unique audit identifier")
    user_id: str = Field(..., description="User performing action")
    username: str = Field(..., description="Username")
    action: AuditAction = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="Resource identifier")
    details: str = Field(..., description="Action details")
    ip_address: str = Field(..., description="Client IP address")
    user_agent: str = Field(..., description="User agent")
    before: Optional[Dict[str, Any]] = Field(None, description="Before state")
    after: Optional[Dict[str, Any]] = Field(None, description="After state")
    success: bool = Field(default=True, description="Action success")
    error_message: Optional[str] = Field(None, description="Error message")
    duration_ms: Optional[float] = Field(None, description="Action duration")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    session_id: Optional[str] = Field(None, description="Session identifier")
    source_module: str = Field(default="UNKNOWN", description="Module performing action")
    
    class Config:
        use_enum_values = True
        
    @validator('audit_id')
    def validate_audit_id(cls, v):
        if not v.startswith('AUD-'):
            raise ValueError('Audit ID must start with AUD-')
        return v

class AuditCreateSchema(BaseModel):
    """Schema for creating an audit log entry"""
    user_id: str
    username: str
    action: AuditAction
    resource_type: str
    resource_id: str
    details: str
    ip_address: str
    user_agent: str
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    source_module: str = "UNKNOWN"