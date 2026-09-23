from src.exceptions import ExternalServiceError, RateLimitedError


class SteamUnavailableError(ExternalServiceError):
    error_code = "steam_unavailable"

    def __init__(self) -> None:
        super().__init__("No se pudo consultar la API de Steam")


class SteamAuthError(ExternalServiceError):
    error_code = "steam_auth_error"

    def __init__(self) -> None:
        super().__init__("Steam rechazó la API key configurada")


class SteamRateLimitedError(RateLimitedError):
    error_code = "steam_rate_limited"

    def __init__(self) -> None:
        super().__init__("Steam está limitando las peticiones")
