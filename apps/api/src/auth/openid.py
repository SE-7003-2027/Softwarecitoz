from urllib.parse import urlencode

import httpx

from src.auth.constants import CLAIMED_ID_RE, REQUIRED_SIGNED, STEAM_OPENID_ENDPOINT
from src.auth.exceptions import OpenIDError


def build_login_url(return_to: str, realm: str) -> str:
    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_to,
        "openid.realm": realm,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }
    return f"{STEAM_OPENID_ENDPOINT}?{urlencode(params)}"


async def verify_callback(
    params: dict[str, str], expected_return_to: str, client: httpx.AsyncClient
) -> str:
    if params.get("openid.mode") != "id_res":
        raise OpenIDError("mode inválido")
    if params.get("openid.op_endpoint") != STEAM_OPENID_ENDPOINT:
        raise OpenIDError("op_endpoint inesperado")
    if params.get("openid.return_to") != expected_return_to:
        raise OpenIDError("return_to no coincide")

    claimed = params.get("openid.claimed_id", "")
    if claimed != params.get("openid.identity"):
        raise OpenIDError("claimed_id e identity difieren")
    match = CLAIMED_ID_RE.match(claimed)
    if not match:
        raise OpenIDError("formato de claimed_id inválido")

    signed = set(params.get("openid.signed", "").split(","))
    if not REQUIRED_SIGNED <= signed:
        raise OpenIDError("faltan campos firmados")

    payload = {k: v for k, v in params.items() if k.startswith("openid.")}
    payload["openid.mode"] = "check_authentication"

    try:
        resp = await client.post(STEAM_OPENID_ENDPOINT, data=payload, timeout=10.0)
    except httpx.RequestError as e:
        raise OpenIDError("Steam no respondió") from e
    if resp.status_code != 200:
        raise OpenIDError(f"Steam respondió {resp.status_code}")
    lines = dict(
        line.split(":", 1) for line in resp.text.splitlines() if ":" in line
    )
    if lines.get("is_valid") != "true":
        raise OpenIDError("Steam no validó la firma")

    return match.group(1)
