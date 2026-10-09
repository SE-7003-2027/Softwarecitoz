class TokenError(Exception):
    pass


class OpenIDError(Exception):
    pass


class RefreshError(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason
