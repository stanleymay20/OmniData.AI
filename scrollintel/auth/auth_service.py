"""
Authentication Service for ScrollIntel
Handles user management, login, and token generation
"""

from typing import Optional
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import os
from datetime import datetime
import json
from pathlib import Path

from .jwt_auth import create_user_token, create_admin_token, create_readonly_token

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_admin: bool = False

class UserInDB(User):
    hashed_password: str

class AuthService:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = Path(users_file)
        self.users: dict[str, UserInDB] = {}
        self._load_users()

    def _load_users(self):
        """Load users from JSON file"""
        if self.users_file.exists():
            with open(self.users_file, "r") as f:
                data = json.load(f)
                for username, user_data in data.items():
                    user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                    if user_data.get("last_login"):
                        user_data["last_login"] = datetime.fromisoformat(user_data["last_login"])
                    self.users[username] = UserInDB(**user_data)

    def _save_users(self):
        """Save users to JSON file"""
        data = {}
        for username, user in self.users.items():
            user_dict = user.dict()
            user_dict["created_at"] = user_dict["created_at"].isoformat()
            if user_dict.get("last_login"):
                user_dict["last_login"] = user_dict["last_login"].isoformat()
            data[username] = user_dict
        
        with open(self.users_file, "w") as f:
            json.dump(data, f, indent=2)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)

    def get_user(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        return self.users.get(username)

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with username and password"""
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user"""
        if self.get_user(user_data.username):
            raise ValueError("Username already exists")

        hashed_password = self.get_password_hash(user_data.password)
        now = datetime.utcnow()
        
        user = UserInDB(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_admin=user_data.is_admin,
            created_at=now
        )
        
        self.users[user.username] = user
        self._save_users()
        return user

    def update_last_login(self, username: str):
        """Update user's last login timestamp"""
        user = self.get_user(username)
        if user:
            user.last_login = datetime.utcnow()
            self._save_users()

    def create_token(self, username: str) -> str:
        """Create appropriate token based on user role"""
        user = self.get_user(username)
        if not user:
            raise ValueError("User not found")
            
        if user.is_admin:
            return create_admin_token(username).access_token
        else:
            return create_user_token(username).access_token

# Create global auth service instance
auth_service = AuthService() 