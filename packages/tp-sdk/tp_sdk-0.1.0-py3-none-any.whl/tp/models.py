from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Visibility Enum
Visibility = Literal['public', 'unlisted', 'private', 'deleted']

class TPBaseModel(BaseModel):
    """Base model that configures camelCase (API) <-> snake_case (Python) mapping."""
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra='ignore' # Ignore extra fields from API to prevent crashes
    )

class Snippet(TPBaseModel):
    """Represents a Snippet fetched from the API."""
    id: str
    title: str
    content: str
    language: str = "plaintext"
    visibility: Visibility
    tags: List[str] = Field(default_factory=list)

    # Metadata
    creator_id: str = Field(alias="creatorId")
    creator_name: str = Field(alias="creatorName", default="Anonymous")
    creator_photo_url: Optional[str] = Field(alias="creatorPhotoURL", default=None)

    # Stats
    view_count: int = Field(alias="viewCount", default=0)
    star_count: int = Field(alias="starCount", default=0)
    copy_count: int = Field(alias="copyCount", default=0)
    is_verified: bool = Field(alias="isVerified", default=False)

    # Pydantic handles ISO string to datetime conversion automatically
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)
    expires_at: Optional[datetime] = Field(alias="expiresAt", default=None)

    # Access logic
    password_bypassed: bool = Field(alias="passwordBypassed", default=False)
    requires_password: bool = Field(alias="requiresPassword", default=False)

class SnippetInput(TPBaseModel):
    """Used for creating or updating a snippet."""
    title: str
    content: str
    language: str = "plaintext"
    visibility: Visibility = "unlisted"
    tags: List[str] = Field(default_factory=list)
    password: str = ""
    # Format expires: "10m", "1h", "1d", "1w" or None
    expires: Optional[str] = None

class SearchResult(TPBaseModel):
    hits: List[Snippet]
    total: int
    took: Optional[int] = None

class UserInfo(TPBaseModel):
    user_id: str = Field(alias="userId")
    display_name: str = Field(alias="displayName")
    photo_url: Optional[str] = Field(alias="photoURL", default=None)
