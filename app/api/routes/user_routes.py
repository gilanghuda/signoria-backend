from fastapi import APIRouter, Depends
from app.model.user import UserResponse
from app.services.user_services import UserService
from app.core.middleware.jwt import get_current_user
from fastapi import HTTPException, status
router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user_id: str = Depends(get_current_user)):
    """Get current user profile"""
    return UserService.get_user(user_id)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by id"""
    return UserService.get_user(user_id)

@router.get("", response_model=list[UserResponse])
async def get_all_users(skip: int = 0, limit: int = 10, _: str = Depends(get_current_user)):
    """Get all users (requires authentication)"""
    return UserService.get_all_users(skip=skip, limit=limit)

@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user_id: str = Depends(get_current_user)):
    """Delete user (only owner or admin)"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other users"
        )
    UserService.delete_user(user_id)
    return {"message": "User deleted successfully"}
