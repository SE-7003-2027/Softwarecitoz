from pwdlib import PasswordHash


_hasher = PasswordHash.recommended()

_dummy_hash = _hasher.hash(
    "chaos-dummy-password-used-only-for-timing"
)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(
    password: str,
    stored_hash: str | None,
) -> bool:

    hash_to_check = stored_hash or _dummy_hash

    valid = _hasher.verify(
        password,
        hash_to_check,
    )

    if stored_hash is None:
        return False

    return valid