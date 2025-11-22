from fastapi import APIRouter, Response
from app.model.user import UserRegister, UserLogin, TokenResponse
from app.services.user_services import UserService

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, response: Response):
    """Register a new user"""
    user, token = UserService.register(user_data, response)
    return TokenResponse(access_token=token, user=user)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, response: Response):
    """Login user and return JWT token"""
    user, token = UserService.login(credentials, response)
    return TokenResponse(access_token=token, user=user)

@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing cookie"""
    return UserService.logout(response)
