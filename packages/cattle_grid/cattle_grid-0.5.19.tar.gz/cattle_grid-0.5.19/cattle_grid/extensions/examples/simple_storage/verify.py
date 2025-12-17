import logging
from urllib.parse import urljoin
import aiohttp

from cattle_grid.extensions import Extension

logger = logging.getLogger(__name__)


async def verify(extension: Extension, session: aiohttp.ClientSession, base_url: str):
    url_to_check = urljoin(base_url, extension.configuration.prefix)  # type: ignore

    async with session.get(url_to_check) as resp:
        if resp.status != 200:
            logger.error("Failed to connect to %s", base_url)
            return False

        text = await resp.text()

        if text != '"simple storage cattle grid sample extension"':
            logger.warning("Got the wrong response")
            logger.warning(text)

        logger.info("Successfully fetched %s", url_to_check)

    return True
