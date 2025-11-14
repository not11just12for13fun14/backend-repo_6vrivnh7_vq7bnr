"""
LibVault Database Schemas

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name.
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# Core domain models
class User(BaseModel):
    full_name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")
    role: Literal["admin", "librarian", "member"] = Field("member")
    is_active: bool = Field(True)
    two_factor_enabled: bool = Field(False)
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    member_id: Optional[str] = Field(None, description="Human-readable member id for Digital Library Card")

class Book(BaseModel):
    isbn: Optional[str] = Field(None, description="ISBN-10/13 if available")
    title: str
    author: str
    publisher: Optional[str] = None
    year: Optional[int] = None
    genres: List[str] = []
    copies_total: int = 1
    copies_available: int = 1
    tags: List[str] = []
    cover_url: Optional[str] = None
    summary: Optional[str] = None

class Transaction(BaseModel):
    user_id: str
    book_id: str
    type: Literal["borrow", "return", "renew"]
    due_date: Optional[datetime] = None
    notes: Optional[str] = None

class Document(BaseModel):
    title: str
    description: Optional[str] = None
    file_url: Optional[str] = Field(None, description="Location of uploaded asset")
    mime_type: Optional[str] = None
    tags: List[str] = []
    version: int = 1
    related_book_id: Optional[str] = None

class Subscription(BaseModel):
    user_id: str
    plan: Literal["free", "pro", "enterprise"] = "free"
    status: Literal["active", "past_due", "canceled"] = "active"
    current_period_end: Optional[datetime] = None
    last_invoice_url: Optional[str] = None

class ForumPost(BaseModel):
    user_id: str
    title: str
    content: str
    tags: List[str] = []
    club_id: Optional[str] = None

class Club(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: str
    member_ids: List[str] = []

class Report(BaseModel):
    name: str
    filters: dict = {}
    generated_url: Optional[str] = None

# Security settings snapshot for Settings page
class SecuritySettings(BaseModel):
    rbac_matrix: dict = {}
    backup_enabled: bool = True
    backup_frequency_days: int = 7
    allow_export: bool = False
    password_policy: dict = {"min_length": 8, "require_symbol": True}
