from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    expertise_level: str = "Intermediate"
    reading_time: int = 15
    interests: List[str] = []

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DiscoveryBase(BaseModel):
    id: str
    title: str
    abstract: str
    primary_domain: str
    significance_score: float
    status: str

class DiscoveryResponse(DiscoveryBase):
    momentum_score: float
    source_urls: List[str]
    authors: List[str]
    first_seen_date: datetime

    class Config:
        from_attributes = True
