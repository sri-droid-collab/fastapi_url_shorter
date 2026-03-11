from datetime import datetime, timezone
from typing import Optional

from pymongo import ReturnDocument

from database import short_urls_collection
from utils import generate_short_code


async def create_short_url(original_url: str) -> dict:
    """Create a new short URL document in MongoDB."""
    # Ensure short code is unique (retry on collision)
    for _ in range(10):
        short_code = generate_short_code()
        if not await short_urls_collection.find_one({"shortCode": short_code}):
            break
    else:
        raise RuntimeError("Failed to generate a unique short code after 10 attempts.")

    now = datetime.now(timezone.utc)
    document = {
        "url": original_url,
        "shortCode": short_code,
        "createdAt": now,
        "updatedAt": now,
        "accessCount": 0,
    }
    result = await short_urls_collection.insert_one(document)
    document["_id"] = result.inserted_id
    return document


async def get_short_url(short_code: str, increment_access: bool = False) -> Optional[dict]:
    """
    Retrieve a short URL document by its short code.
    If increment_access is True, atomically increment accessCount.
    """
    if increment_access:
        document = await short_urls_collection.find_one_and_update(
            {"shortCode": short_code},
            {"$inc": {"accessCount": 1}},
            return_document=ReturnDocument.AFTER,
        )
    else:
        document = await short_urls_collection.find_one({"shortCode": short_code})
    return document


async def update_short_url(short_code: str, new_url: str) -> Optional[dict]:
    """Update the URL of an existing short URL document."""
    now = datetime.now(timezone.utc)
    document = await short_urls_collection.find_one_and_update(
        {"shortCode": short_code},
        {"$set": {"url": new_url, "updatedAt": now}},
        return_document=ReturnDocument.AFTER,
    )
    return document


async def delete_short_url(short_code: str) -> bool:
    """Delete a short URL document. Returns True if deleted, False if not found."""
    result = await short_urls_collection.delete_one({"shortCode": short_code})
    return result.deleted_count == 1
