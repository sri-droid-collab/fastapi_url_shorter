import motor.motor_asyncio

from app.core.config import settings

# Create the async MongoDB client once — reuse it across the whole app
client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGODB_URL,
    tls=True,
    tlsAllowInvalidCertificates=False,
)

db = client[settings.DATABASE_NAME]

# Collections — add new ones here as the project grows
short_urls_collection = db.get_collection("short_urls")
