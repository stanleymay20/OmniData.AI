"""
JWT Authentication Module for ScrollIntel
Handles token generation, validation, and dependency injection for FastAPI endpoints
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")  # Change in production
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class TokenData(BaseModel):
    username: Optional[str] = None
    permissions: Optional[list[str]] = None

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token
    
    Args:
        data: Dictionary containing token payload
        expires_delta: Optional expiration time delta
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """
    Validate JWT token and return user data
    
    Args:
        credentials: HTTP Authorization credentials containing the JWT token
        
    Returns:
        TokenData: User data from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        permissions: list[str] = payload.get("permissions", [])
        
        if username is None:
            raise credentials_exception
            
        return TokenData(username=username, permissions=permissions)
    except jwt.PyJWTError:
        raise credentials_exception

def require_permission(required_permission: str):
    """
    Dependency to check if user has required permission
    
    Args:
        required_permission: Permission string to check for
        
    Returns:
        Callable: Dependency function
    """
    async def permission_dependency(user: TokenData = Depends(get_current_user)):
        if required_permission not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
    return permission_dependency

# Common permission sets
ADMIN_PERMISSIONS = ["admin", "read", "write", "delete"]
USER_PERMISSIONS = ["read", "write"]
READ_ONLY_PERMISSIONS = ["read"]

def create_admin_token(username: str) -> Token:
    """Create an admin token with full permissions"""
    access_token = create_access_token(
        data={"sub": username, "permissions": ADMIN_PERMISSIONS}
    )
    return Token(access_token=access_token, token_type="bearer")

def create_user_token(username: str) -> Token:
    """Create a regular user token with standard permissions"""
    access_token = create_access_token(
        data={"sub": username, "permissions": USER_PERMISSIONS}
    )
    return Token(access_token=access_token, token_type="bearer")

def create_readonly_token(username: str) -> Token:
    """Create a read-only token"""
    access_token = create_access_token(
        data={"sub": username, "permissions": READ_ONLY_PERMISSIONS}
    )
    return Token(access_token=access_token, token_type="bearer") 