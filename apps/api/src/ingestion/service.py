import logging

logger = logging.getLogger(__name__)


async def enqueue_express_ingest(steamid: str) -> None:
    logger.info("express_ingest_enqueued steamid=%s", steamid)
