import json
import os

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from freezegun import freeze_time

from src.auth.config import get_auth_settings
from src.auth.exceptions import TokenError
from src.auth.tokens import issue_access, issue_openid_state, verify_access


def _pem_pair() -> tuple[str, str]:
    key = Ed25519PrivateKey.generate()
    private = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private, public


@pytest.fixture
def restore_auth_env():
    saved = {k: os.environ[k] for k in ("JWT_ACTIVE_KID", "JWT_PRIVATE_KEY_PEM", "JWT_PUBLIC_KEYS_JSON")}
    yield
    os.environ.update(saved)
    get_auth_settings.cache_clear()


def test_roundtrip_has_expected_claims():
    claims = verify_access(issue_access(7, "fam-1", ["user"]))
    assert claims["sub"] == "7"
    assert claims["sid"] == "fam-1"
    assert claims["typ"] == "access"
    assert claims["roles"] == ["user"]


def test_access_valid_within_leeway():
    with freeze_time("2026-10-01 12:00:00"):
        access = issue_access(1, "fam-1", ["user"])
    with freeze_time("2026-10-01 12:15:20"):
        assert verify_access(access)["sub"] == "1"


def test_access_expires_after_ttl():
    with freeze_time("2026-10-01 12:00:00"):
        access = issue_access(1, "fam-1", ["user"])
    with freeze_time("2026-10-01 12:16:00"):
        with pytest.raises(TokenError, match="expired"):
            verify_access(access)


def test_state_token_cannot_be_used_as_access():
    with pytest.raises(TokenError):
        verify_access(issue_openid_state("n", "/"))


def test_rejects_alg_none():
    forged = jwt.encode({"sub": "1", "typ": "access"}, key=None, algorithm="none")
    with pytest.raises(TokenError):
        verify_access(forged)


def test_rejects_tampered_signature():
    header, payload, sig = issue_access(1, "fam-1", ["user"]).split(".")
    tampered_sig = ("A" if sig[0] != "A" else "B") + sig[1:]
    with pytest.raises(TokenError):
        verify_access(f"{header}.{payload}.{tampered_sig}")


def test_rejects_unknown_kid():
    private, _ = _pem_pair()
    forged = jwt.encode(
        {"sub": "1", "typ": "access"}, private, algorithm="EdDSA", headers={"kid": "../etc/passwd"}
    )
    with pytest.raises(TokenError, match="invalid"):
        verify_access(forged)


def test_key_rotation(restore_auth_env):
    old_token = issue_access(1, "fam-1", ["user"])
    old_public = get_auth_settings().public_keys["test"]
    new_private, new_public = _pem_pair()

    os.environ["JWT_ACTIVE_KID"] = "next"
    os.environ["JWT_PRIVATE_KEY_PEM"] = new_private
    os.environ["JWT_PUBLIC_KEYS_JSON"] = json.dumps({"test": old_public, "next": new_public})
    get_auth_settings.cache_clear()

    assert verify_access(old_token)["sub"] == "1"
    assert verify_access(issue_access(2, "fam-2", ["user"]))["sub"] == "2"

    os.environ["JWT_PUBLIC_KEYS_JSON"] = json.dumps({"next": new_public})
    get_auth_settings.cache_clear()

    with pytest.raises(TokenError):
        verify_access(old_token)
