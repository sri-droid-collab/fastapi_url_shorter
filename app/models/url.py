from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Field


# ── Request Schemas ───────────────────────────────────────────────────────────

class URLCreateRequest(BaseModel):
    """Payload required to create a new short URL."""
    url: HttpUrl = Field(..., examples=["https://www.example.com/some/long/url"])


class URLUpdateRequest(BaseModel):
    """Payload required to update an existing short URL."""
    url: HttpUrl = Field(..., examples=["https://www.example.com/some/updated/url"])


# ── Response Schemas ──────────────────────────────────────────────────────────

class URLResponse(BaseModel):
    """Standard response for a single short URL record."""
    id: str
    url: str
    shortCode: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True


class URLStatsResponse(URLResponse):
    """Extends URLResponse with access count statistics."""
    accessCount: int


class URLListResponse(BaseModel):
    """Response wrapper for listing all short URLs."""
    total: int
    urls: List[URLResponse]


# ── Internal Helpers ──────────────────────────────────────────────────────────

def url_document_to_response(doc: dict) -> dict:
    """Convert a raw MongoDB document into a URLResponse-compatible dict."""
    return {
        "id": str(doc["_id"]),
        "url": doc["url"],
        "shortCode": doc["shortCode"],
        "createdAt": doc["createdAt"],
        "updatedAt": doc["updatedAt"],
    }


def url_document_to_stats_response(doc: dict) -> dict:
    """Convert a raw MongoDB document into a URLStatsResponse-compatible dict."""
    base = url_document_to_response(doc)
    base["accessCount"] = doc.get("accessCount", 0)
    return base
