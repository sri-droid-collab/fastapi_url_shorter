from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


# ── Request schemas ──────────────────────────────────────────────────────────

class URLCreateRequest(BaseModel):
    url: HttpUrl = Field(..., examples=["https://www.example.com/some/long/url"])


class URLUpdateRequest(BaseModel):
    url: HttpUrl = Field(..., examples=["https://www.example.com/some/updated/url"])


# ── Response schemas ─────────────────────────────────────────────────────────

class URLResponse(BaseModel):
    id: str
    url: str
    shortCode: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        populate_by_name = True


class URLStatsResponse(URLResponse):
    accessCount: int


# ── Internal helper ──────────────────────────────────────────────────────────

def url_document_to_response(doc: dict) -> dict:
    """Convert a MongoDB document to a dict suitable for URLResponse."""
    return {
        "id": str(doc["_id"]),
        "url": doc["url"],
        "shortCode": doc["shortCode"],
        "createdAt": doc["createdAt"],
        "updatedAt": doc["updatedAt"],
    }


def url_document_to_stats_response(doc: dict) -> dict:
    """Convert a MongoDB document to a dict suitable for URLStatsResponse."""
    base = url_document_to_response(doc)
    base["accessCount"] = doc.get("accessCount", 0)
    return base
