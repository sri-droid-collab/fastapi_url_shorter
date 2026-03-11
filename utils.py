import secrets
import string

SHORT_CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits  # A-Z, a-z, 0-9


def generate_short_code() -> str:
    """Generate a cryptographically random 6-character short code."""
    return "".join(secrets.choice(ALPHABET) for _ in range(SHORT_CODE_LENGTH))
