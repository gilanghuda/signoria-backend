from fastapi import HTTPException, status, Response
from app.model.user import UserRegister, UserLogin, UserResponse
from app.repository.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token

class UserService:
    @staticmethod
    def _set_auth_cookie(response: Response, token: str) -> None:
        """Set JWT token in HTTP-only cookie"""
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=True,  
            samesite="none",
            max_age=86400  # 24 hours
        )
    
    @staticmethod
    def _clear_auth_cookie(response: Response) -> None:
        """Clear JWT token from cookie"""
        response.delete_cookie(key="access_token")
    
    @staticmethod
    def register(user_data: UserRegister, response: Response) -> tuple[UserResponse, str]:
        """Register a new user and return user data and token"""
        # Check if email already exists
        existing_email = UserRepository.get_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = UserRepository.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user in database
        user = UserRepository.create(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Generate JWT token
        token = create_access_token(user["id"])
        
        # Set auth cookie
        UserService._set_auth_cookie(response, token)
        
        user_response = UserResponse(**user)
        return user_response, token
    
    @staticmethod
    def login(credentials: UserLogin, response: Response) -> tuple[UserResponse, str]:
        """Authenticate user and return user data and token"""
        # Get user by email
        user = UserRepository.get_by_email(credentials.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT token
        token = create_access_token(user["id"])
        
        # Set auth cookie
        UserService._set_auth_cookie(response, token)
        
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
        
        return user_response, token
    
    @staticmethod
    def logout(response: Response) -> dict:
        """Logout user by clearing cookie"""
        UserService._clear_auth_cookie(response)
        return {"message": "Logged out successfully"}
    
    @staticmethod
    def get_user(user_id: str) -> UserResponse:
        """Get user by id"""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(**user)
    
    @staticmethod
    def get_all_users(skip: int = 0, limit: int = 10) -> list[UserResponse]:
        """Get all users with pagination"""
        users = UserRepository.get_all(skip=skip, limit=limit)
        return [UserResponse(**user) for user in users]
    
    @staticmethod
    def update_user(user_id: str, **kwargs) -> UserResponse:
        """Update user fields"""
        user = UserRepository.update(user_id, **kwargs)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(**user)
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """Delete user"""
        result = UserRepository.delete(user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return True
