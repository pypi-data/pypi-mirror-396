from typing import Optional, List, Any, Dict, Literal
from pydantic import BaseModel, Field


class SDKConfig(BaseModel):
    """Configuration for the MemoryClient."""
    api_key: str = Field(..., description="Your Cluster Access Key (sk_live_...)")
    base_url: str = Field(default="https://api.memorymodel.dev", description="API base URL")
    default_end_user_id: Optional[str] = Field(default=None, description="Default end user ID")


class TextSource(BaseModel):
    type: Literal["text"] = "text"
    content: str = Field(..., min_length=1, description="Text content to ingest")


class TextIngestPayload(BaseModel):
    source: TextSource
    user_context: Optional[str] = Field(default=None, alias="userContext")

    class Config:
        populate_by_name = True


class ImageIngestPayload(BaseModel):
    image_data: str = Field(..., min_length=10, alias="imageData", description="Base64 encoded image")
    user_context: Optional[str] = Field(default=None, alias="userContext")

    class Config:
        populate_by_name = True


class SearchOptions(BaseModel):
    limit: int = Field(default=5, gt=0)


class SearchPayload(BaseModel):
    query: str = Field(..., min_length=1)
    use_dynamic_scoring: bool = Field(default=True, alias="useDynamicScoring")
    strategy: Literal["centroid_aware", "simple"] = "centroid_aware"
    options: Optional[SearchOptions] = None

    class Config:
        populate_by_name = True


class MemoryItem(BaseModel):
    id: str
    content: Optional[str] = None  # Optional: backend may return different structures
    similarity: Optional[float] = None
    # Allow extra fields
    class Config:
        extra = "allow"


class IngestResponse(BaseModel):
    status: str
    job_id: str = Field(..., alias="jobId")
    preview_url: Optional[str] = Field(default=None, alias="previewUrl")

    class Config:
        populate_by_name = True


class SearchResponse(BaseModel):
    data: List[MemoryItem]


class ListMemoryResponse(BaseModel):
    data: List[MemoryItem]
