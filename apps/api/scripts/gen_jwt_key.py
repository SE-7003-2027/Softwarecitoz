import json
import sys
from datetime import UTC, datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

kid = sys.argv[1] if len(sys.argv) > 1 else datetime.now(UTC).strftime("%Y-%m")
key = Ed25519PrivateKey.generate()

private_pem = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.NoEncryption(),
).decode()
public_pem = key.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()

print(f"JWT_ACTIVE_KID={kid}")
print(f'JWT_PRIVATE_KEY_PEM="{private_pem.strip()}"')
print(f"JWT_PUBLIC_KEYS_JSON={json.dumps({kid: public_pem})}")
