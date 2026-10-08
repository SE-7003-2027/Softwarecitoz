import httpx
import pytest
import respx

from src.auth.constants import STEAM_OPENID_ENDPOINT
from src.auth.exceptions import OpenIDError
from src.auth.openid import build_login_url, verify_callback

RETURN_TO = "https://tuapp.com/auth/steam/callback?state=s1"
STEAMID = "76561198002516729"


def callback_params(return_to: str = RETURN_TO, steamid: str = STEAMID) -> dict:
    cid = f"https://steamcommunity.com/openid/id/{steamid}"
    return {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "id_res",
        "openid.op_endpoint": STEAM_OPENID_ENDPOINT,
        "openid.claimed_id": cid,
        "openid.identity": cid,
        "openid.return_to": return_to,
        "openid.response_nonce": "2026-10-01T16:20:00Zabc",
        "openid.assoc_handle": "1234567890",
        "openid.signed": "signed,op_endpoint,claimed_id,identity,return_to,response_nonce,assoc_handle",
        "openid.sig": "SIGNATURE==",
    }


def test_login_url_points_to_steam():
    url = httpx.URL(build_login_url(RETURN_TO, "https://tuapp.com"))
    assert str(url).startswith(STEAM_OPENID_ENDPOINT)
    assert url.params["openid.mode"] == "checkid_setup"
    assert url.params["openid.return_to"] == RETURN_TO
    assert url.params["openid.realm"] == "https://tuapp.com"


@respx.mock
async def test_valid_callback_forwards_signature():
    params = callback_params()

    def steam_side(request: httpx.Request):
        body = dict(httpx.QueryParams(request.content.decode()))
        assert body["openid.mode"] == "check_authentication"
        assert body["openid.sig"] == params["openid.sig"]
        assert body["openid.response_nonce"] == params["openid.response_nonce"]
        assert body["openid.signed"] == params["openid.signed"]
        assert "state" not in body
        return httpx.Response(200, text="ns:http://specs.openid.net/auth/2.0\nis_valid:true\n")

    respx.post(STEAM_OPENID_ENDPOINT).mock(side_effect=steam_side)
    async with httpx.AsyncClient() as c:
        assert await verify_callback(params | {"state": "s1"}, RETURN_TO, c) == STEAMID


@respx.mock
async def test_rejects_when_steam_says_invalid():
    respx.post(STEAM_OPENID_ENDPOINT).mock(
        return_value=httpx.Response(200, text="ns:http://specs.openid.net/auth/2.0\nis_valid:false\n")
    )
    async with httpx.AsyncClient() as c:
        with pytest.raises(OpenIDError):
            await verify_callback(callback_params(), RETURN_TO, c)


@respx.mock
async def test_rejects_when_steam_errors():
    respx.post(STEAM_OPENID_ENDPOINT).mock(return_value=httpx.Response(503))
    async with httpx.AsyncClient() as c:
        with pytest.raises(OpenIDError):
            await verify_callback(callback_params(), RETURN_TO, c)


@pytest.mark.parametrize(
    "overrides",
    [
        {"openid.mode": "cancel"},
        {"openid.op_endpoint": "https://evil.example/openid"},
        {"openid.return_to": "https://evil.example/auth/steam/callback?state=s1"},
        {"openid.identity": "https://steamcommunity.com/openid/id/76561198000000000"},
        {
            "openid.claimed_id": "https://steamcommunity.com/openid/id/123",
            "openid.identity": "https://steamcommunity.com/openid/id/123",
        },
        {
            "openid.claimed_id": f"https://evil.example/openid/id/{STEAMID}",
            "openid.identity": f"https://evil.example/openid/id/{STEAMID}",
        },
        {"openid.signed": "signed,op_endpoint,claimed_id,identity,return_to,assoc_handle"},
    ],
    ids=[
        "cancel",
        "foreign_op_endpoint",
        "foreign_return_to",
        "claimed_id_differs_from_identity",
        "short_steamid",
        "foreign_claimed_id_host",
        "nonce_not_signed",
    ],
)
@respx.mock
async def test_rejects_invalid_callbacks_without_calling_steam(overrides):
    route = respx.post(STEAM_OPENID_ENDPOINT).mock(
        return_value=httpx.Response(200, text="is_valid:true\n")
    )
    async with httpx.AsyncClient() as c:
        with pytest.raises(OpenIDError):
            await verify_callback(callback_params() | overrides, RETURN_TO, c)
    assert not route.called
