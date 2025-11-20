"""
Database Schemas for CampusLink

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name.

Entities:
- User: students, professors, companies (role-based)
- Post: questions, internship requests, discussion
- Comment: threaded discussion on posts
- Offer: internship offers posted by companies or attached to a post
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal


Role = Literal["student", "professor", "company"]
PostType = Literal["question", "internship_request", "discussion"]


class User(BaseModel):
    """
    Users collection schema
    Collection: "user"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    role: Role = Field(..., description="Role in the platform")
    college: Optional[str] = Field(None, description="College/University name")
    department: Optional[str] = Field(None, description="Department (for students/professors)")
    company_name: Optional[str] = Field(None, description="Company name (for company role)")
    headline: Optional[str] = Field(None, description="Short bio or headline")
    verified: bool = Field(False, description="Whether the account is verified by admins")


class Post(BaseModel):
    """
    Posts collection schema
    Collection: "post"
    """
    type: PostType = Field(..., description="Type of post")
    title: str = Field(..., description="Short title of the post")
    content: str = Field(..., description="Body content")
    tags: List[str] = Field(default_factory=list, description="Topic tags")
    created_by: str = Field(..., description="User ID string of the author")


class Comment(BaseModel):
    """
    Comments collection schema
    Collection: "comment"
    """
    post_id: str = Field(..., description="Post ID this comment belongs to")
    content: str = Field(..., description="Comment text")
    created_by: str = Field(..., description="User ID string of the author")
    parent_id: Optional[str] = Field(None, description="Parent comment ID for threads")


class Offer(BaseModel):
    """
    Offers collection schema
    Collection: "offer"
    """
    title: str = Field(..., description="Internship title")
    description: str = Field(..., description="Internship description")
    location: Optional[str] = Field(None, description="Location or Remote")
    stipend: Optional[str] = Field(None, description="Compensation details")
    post_id: Optional[str] = Field(None, description="Related post ID if any")
    created_by: str = Field(..., description="User ID string of the company poster")


# Note: The viewer may read these via /schema endpoint if exposed by the backend.
