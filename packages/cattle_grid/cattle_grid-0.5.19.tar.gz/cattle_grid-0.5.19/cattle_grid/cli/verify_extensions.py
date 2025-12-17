import logging
import aiohttp
from cattle_grid.extensions import Extension

logger = logging.getLogger(__name__)


async def verify_extensions(extensions: list[Extension], base_urls: list[str]):
    success = True
    async with aiohttp.ClientSession() as session:
        for extension in extensions:
            if extension.verify:
                failed_base_urls = []
                for base_url in base_urls:
                    result = await extension.verify(extension, session, base_url)
                    if not result:
                        logger.error(
                            "Failed verification for extension %s and url %s",
                            extension.name,
                            base_url,
                        )
                        success = False
                        failed_base_urls.append(base_url)

                if len(failed_base_urls) > 0:
                    logger.warning(
                        "Failed verification for %s on %s",
                        extension.name,
                        ", ".join(failed_base_urls),
                    )

    return success
