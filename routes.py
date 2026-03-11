from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

import crud
from models import (
    URLCreateRequest,
    URLUpdateRequest,
    URLResponse,
    URLStatsResponse,
    url_document_to_response,
    url_document_to_stats_response,
)

router = APIRouter()


# ── 1. Create Short URL ───────────────────────────────────────────────────────

@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a short URL",
    tags=["URL Shortener"],
)
async def create_short_url(payload: URLCreateRequest):
    """
    Accept a long URL and return a shortened version with a unique 6-character code.
    """
    document = await crud.create_short_url(str(payload.url))
    return url_document_to_response(document)


# ── 2. Retrieve Original URL ──────────────────────────────────────────────────

@router.get(
    "/shorten/{short_code}",
    response_model=URLResponse,
    summary="Retrieve original URL by short code",
    tags=["URL Shortener"],
)
async def get_short_url(short_code: str):
    """
    Look up the original URL by its short code and increment the access counter.
    """
    document = await crud.get_short_url(short_code, increment_access=True)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return url_document_to_response(document)


# ── 3. Update Short URL ───────────────────────────────────────────────────────

@router.put(
    "/shorten/{short_code}",
    response_model=URLResponse,
    summary="Update the URL for a short code",
    tags=["URL Shortener"],
)
async def update_short_url(short_code: str, payload: URLUpdateRequest):
    """
    Replace the long URL associated with an existing short code.
    Updates the `updatedAt` timestamp.
    """
    document = await crud.update_short_url(short_code, str(payload.url))
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return url_document_to_response(document)


# ── 4. Delete Short URL ───────────────────────────────────────────────────────

@router.delete(
    "/shorten/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a short URL",
    tags=["URL Shortener"],
)
async def delete_short_url(short_code: str):
    """
    Permanently remove a short URL record from the database.
    """
    deleted = await crud.delete_short_url(short_code)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )


# ── 5. URL Statistics ─────────────────────────────────────────────────────────

@router.get(
    "/shorten/{short_code}/stats",
    response_model=URLStatsResponse,
    summary="Get access statistics for a short URL",
    tags=["URL Shortener"],
)
async def get_url_stats(short_code: str):
    """
    Return URL metadata including total access count (does NOT increment it).
    """
    document = await crud.get_short_url(short_code, increment_access=False)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return url_document_to_stats_response(document)


# ── BONUS: Redirect Endpoint ──────────────────────────────────────────────────

@router.get(
    "/r/{short_code}",
    status_code=status.HTTP_302_FOUND,
    summary="Redirect to the original URL (bonus)",
    tags=["Redirect"],
)
async def redirect_to_url(short_code: str):
    """
    Redirect the browser to the original URL associated with the short code.
    Increments the access counter on each visit.
    """
    document = await crud.get_short_url(short_code, increment_access=True)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return RedirectResponse(url=document["url"], status_code=status.HTTP_302_FOUND)
