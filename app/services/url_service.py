from datetime import datetime, timezone
from typing import Optional

from pymongo import ReturnDocument

from app.db.database import short_urls_collection
from app.utils.shortcode import generate_short_code


async def create_url(original_url: str) -> dict:
    """
    Insert a new short URL document into the database.

    Retries up to 10 times to guarantee the generated short code is unique.
    Raises RuntimeError if all 10 attempts produce a collision (extremely unlikely).
    """
    for _ in range(10):
        short_code = generate_short_code()
        if not await short_urls_collection.find_one({"shortCode": short_code}):
            break
    else:
        raise RuntimeError("Could not generate a unique short code after 10 attempts.")

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


async def get_url_by_code(short_code: str, increment_access: bool = False) -> Optional[dict]:
    """
    Find a short URL document by its short code.

    Pass increment_access=True when the user is actually visiting the link
    so the access counter is bumped atomically.
    """
    if increment_access:
        return await short_urls_collection.find_one_and_update(
            {"shortCode": short_code},
            {"$inc": {"accessCount": 1}},
            return_document=ReturnDocument.AFTER,
        )
    return await short_urls_collection.find_one({"shortCode": short_code})


async def get_all_urls() -> list[dict]:
    """
    Return all short URL documents, ordered by creation date (newest first).
    """
    cursor = short_urls_collection.find().sort("createdAt", -1)
    return await cursor.to_list(length=None)


async def update_url(short_code: str, new_url: str) -> Optional[dict]:
    """
    Replace the long URL stored under an existing short code.
    Also updates the updatedAt timestamp.
    """
    now = datetime.now(timezone.utc)
    return await short_urls_collection.find_one_and_update(
        {"shortCode": short_code},
        {"$set": {"url": new_url, "updatedAt": now}},
        return_document=ReturnDocument.AFTER,
    )


async def delete_url(short_code: str) -> bool:
    """
    Delete the document for a given short code.
    Returns True if a document was deleted, False if nothing was found.
    """
    result = await short_urls_collection.delete_one({"shortCode": short_code})
    return result.deleted_count == 1
