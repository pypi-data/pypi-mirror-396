import pytest
import click

from dynaconf.utils import DynaconfDict

from click.testing import CliRunner

from .verify import add_verify_commands


@pytest.fixture
def config():
    settings = DynaconfDict(
        {
            "db_url": "some",
            "amqp_url": "some",
            "frontend": {"base_urls": ["http://host.test"]},
        }
    )
    return settings


@pytest.fixture
def cli(tmp_path, config):
    @click.group()
    @click.pass_context
    def main(ctx):
        ctx.ensure_object(dict)
        ctx.obj["config"] = config

    add_verify_commands(main)

    return main


@pytest.mark.parametrize("command", ["base-urls", "extensions"])
def test_basic_commands(cli, command):
    result = CliRunner().invoke(cli, ["verify", command, "--dry-run"])

    assert result.exit_code == 0
