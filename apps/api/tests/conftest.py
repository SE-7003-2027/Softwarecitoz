import json
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

_key = Ed25519PrivateKey.generate()
os.environ["BASE_URL"] = "https://tuapp.com"
os.environ["STEAM_API_KEY"] = "test-steam-key"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
os.environ["JWT_ACTIVE_KID"] = "test"
os.environ["JWT_PRIVATE_KEY_PEM"] = _key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
).decode()
os.environ["JWT_PUBLIC_KEYS_JSON"] = json.dumps(
    {
        "test": _key.public_key()
        .public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    }
)
