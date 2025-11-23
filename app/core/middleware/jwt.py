from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency to extract current user from JWT token.
    Tries in order:
    1. HTTP-only cookie (access_token)
    2. Authorization header (Bearer token)
    
    Returns:
        str: user_id extracted from JWT token
        
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    token = None
    
    # Priority 1: Try to get token from HTTP-only cookies
    token = request.cookies.get("access_token")
    
    # Priority 2: Try to get token from Authorization header
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Missing access token in cookies or Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = decode_access_token(token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
