import motor.motor_asyncio
from config import settings

# MongoDB Atlas requires TLS; local connections work fine with these flags too.
client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGODB_URL,
    tls=True,
    tlsAllowInvalidCertificates=False,
)
db = client[settings.DATABASE_NAME]

# Collection
short_urls_collection = db.get_collection("short_urls")
