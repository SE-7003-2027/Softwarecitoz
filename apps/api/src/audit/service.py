import logging

logger = logging.getLogger("audit")


async def audit_log(event: str, **fields) -> None:
    logger.info(
        "%s %s",
        event,
        " ".join(f"{k}={v}" for k, v in fields.items() if v is not None),
    )
