from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from app.services import url_service
from app.models.url import (
    URLCreateRequest,
    URLUpdateRequest,
    URLResponse,
    URLStatsResponse,
    URLListResponse,
    url_document_to_response,
    url_document_to_stats_response,
)

router = APIRouter()


# ── 1. List All URLs ──────────────────────────────────────────────────────────

@router.get(
    "/shorten",
    response_model=URLListResponse,
    summary="List all short URLs",
    tags=["URL Shortener"],
)
async def list_all_urls():
    """
    Return every short URL stored in the database, sorted newest first.
    The response includes a `total` count and a `urls` array.
    """
    documents = await url_service.get_all_urls()
    return {
        "total": len(documents),
        "urls": [url_document_to_response(doc) for doc in documents],
    }


# ── 2. Create Short URL ───────────────────────────────────────────────────────

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
    document = await url_service.create_url(str(payload.url))
    return url_document_to_response(document)


# ── 3. Get One Short URL ──────────────────────────────────────────────────────

@router.get(
    "/shorten/{short_code}",
    response_model=URLResponse,
    summary="Retrieve original URL by short code",
    tags=["URL Shortener"],
)
async def get_short_url(short_code: str):
    """
    Look up the original URL by its short code.
    Each call increments the access counter.
    """
    document = await url_service.get_url_by_code(short_code, increment_access=True)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return url_document_to_response(document)


# ── 4. Update Short URL ───────────────────────────────────────────────────────

@router.put(
    "/shorten/{short_code}",
    response_model=URLResponse,
    summary="Update the URL for a short code",
    tags=["URL Shortener"],
)
async def update_short_url(short_code: str, payload: URLUpdateRequest):
    """
    Replace the long URL associated with an existing short code.
    The `updatedAt` timestamp is automatically refreshed.
    """
    document = await url_service.update_url(short_code, str(payload.url))
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return url_document_to_response(document)


# ── 5. Delete Short URL ───────────────────────────────────────────────────────

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
    deleted = await url_service.delete_url(short_code)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )


# ── 6. Get URL Statistics ─────────────────────────────────────────────────────

@router.get(
    "/shorten/{short_code}/stats",
    response_model=URLStatsResponse,
    summary="Get access statistics for a short URL",
    tags=["URL Shortener"],
)
async def get_url_stats(short_code: str):
    """
    Return URL metadata including the total access count.
    This call does NOT increment the counter.
    """
    document = await url_service.get_url_by_code(short_code, increment_access=False)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return url_document_to_stats_response(document)


# ── 7. Redirect ───────────────────────────────────────────────────────────────

@router.get(
    "/r/{short_code}",
    status_code=status.HTTP_302_FOUND,
    summary="Redirect to the original URL",
    tags=["Redirect"],
)
async def redirect_to_url(short_code: str):
    """
    Redirect the browser directly to the original long URL.
    Increments the access counter on each visit.
    """
    document = await url_service.get_url_by_code(short_code, increment_access=True)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found.",
        )
    return RedirectResponse(url=document["url"], status_code=status.HTTP_302_FOUND)
