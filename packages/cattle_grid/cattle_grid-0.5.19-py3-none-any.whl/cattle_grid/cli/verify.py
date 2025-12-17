import asyncio
import logging
import aiohttp
import click

from cattle_grid.app import app_globals
from .verify_extensions import verify_extensions
from ..app.extensions import init_extensions


logger = logging.getLogger(__name__)


async def verify_connectivity(base_urls: list[str]):
    async with aiohttp.ClientSession() as session:
        for x in base_urls:
            logger.info("Verifying connectivity for %s", x)
            url = f"{x}/.well-known/nodeinfo"
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Got status {response.status} for {url}")
                content_type = response.headers["content-type"]
                if content_type != "application/jrd+json":
                    logger.warning(f"Got content type {content_type} for {url}")


def add_verify_commands(main: click.Group):
    @main.group()
    def verify(): ...

    @verify.command()
    @click.option("--dry-run", default=False, is_flag=True)
    @click.pass_context
    def base_urls(ctx, dry_run):
        """verifies the installation. Current checks that the base_urls have a correctly configured nodeinfo response"""

        base_urls = app_globals.application_config.frontend_config.base_urls

        if not dry_run:
            asyncio.run(verify_connectivity(base_urls))
        else:
            logger.info("Got base urls %s", ", ".join(base_urls))

    @verify.command()
    @click.option("--dry-run", default=False, is_flag=True)
    def extensions(dry_run):
        extensions = init_extensions(app_globals.config)

        logger.info("Successfully loaded %d extensions", len(extensions))
        base_urls = app_globals.application_config.frontend_config.base_urls

        if not dry_run:
            asyncio.run(verify_extensions(extensions, base_urls))
