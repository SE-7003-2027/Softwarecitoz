import logging
import re

KEY_RE = re.compile(r"(key=)[^&\s\"]+", re.IGNORECASE)


class RedactSecrets(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = KEY_RE.sub(r"\1REDACTED", record.getMessage())
        record.args = ()
        return True


def setup_logging(level: str = "info") -> None:
    logging.basicConfig(level=level.upper())
    for handler in logging.getLogger().handlers:
        handler.addFilter(RedactSecrets())
