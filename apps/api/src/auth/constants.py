import re

STEAM_OPENID_ENDPOINT = "https://steamcommunity.com/openid/login"
CLAIMED_ID_RE = re.compile(r"^https://steamcommunity\.com/openid/id/(\d{17})$")
REQUIRED_SIGNED = frozenset(
    {
        "op_endpoint",
        "claimed_id",
        "identity",
        "return_to",
        "response_nonce",
        "assoc_handle",
    }
)
CALLBACK_PATH = "/auth/steam/callback"

ACCESS_AUD = "steam-insights-api"
STATE_AUD = "steam-insights-openid-state"
JWT_ALGORITHMS = ["EdDSA"]

ACCESS_COOKIE = "__Host-at"
REFRESH_COOKIE = "__Secure-rt"
STATE_COOKIE = "__Host-oid"
REFRESH_PATH = "/auth"

REFRESH_TOKEN_PREFIX = "rt_"
