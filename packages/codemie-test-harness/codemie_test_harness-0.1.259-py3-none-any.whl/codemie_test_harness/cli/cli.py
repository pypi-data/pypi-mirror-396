"""Main CLI entry point for CodeMie Test Harness.

Thin entry point: registers commands and wires common options.
"""

from __future__ import annotations

import os
from typing import Optional

import click

from .constants import (
    CONTEXT_SETTINGS,
    KEY_AUTH_SERVER_URL,
    KEY_AUTH_CLIENT_ID,
    KEY_AUTH_CLIENT_SECRET,
    KEY_AUTH_REALM_NAME,
    KEY_CODEMIE_API_DOMAIN,
    KEY_AUTH_USERNAME,
    KEY_AUTH_PASSWORD,
)
from .utils import ensure_env_from_config
from .commands.config_cmd import config_cmd
from .commands.run_cmd import run_cmd
from .commands.assistant_cmd import assistant_cmd
from .commands.workflow_cmd import workflow_cmd
from .commands.marks_cmd import marks_cmd


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--auth-server-url", envvar=KEY_AUTH_SERVER_URL, help="Auth server url")
@click.option("--auth-client-id", envvar=KEY_AUTH_CLIENT_ID, help="Auth client id")
@click.option(
    "--auth-client-secret", envvar=KEY_AUTH_CLIENT_SECRET, help="Auth client secret"
)
@click.option("--auth-realm-name", envvar=KEY_AUTH_REALM_NAME, help="Auth realm name")
@click.option("--auth-username", envvar=KEY_AUTH_USERNAME, help="Auth username")
@click.option("--auth-password", envvar=KEY_AUTH_PASSWORD, help="Auth password")
@click.option(
    "--api-domain", envvar=KEY_CODEMIE_API_DOMAIN, help="CodeMie API domain URL"
)
# Integration credentials are set via 'codemie-test-harness config set' command
@click.pass_context
def cli(
    ctx: click.Context,
    auth_server_url: Optional[str],
    auth_client_id: Optional[str],
    auth_client_secret: Optional[str],
    auth_realm_name: Optional[str],
    auth_username: Optional[str],
    auth_password: Optional[str],
    api_domain: Optional[str],
):
    """CodeMie Test Harness CLI.

    Available commands: config, run, assistant, workflow, marks

    Integration credentials should be set using:
      codemie-test-harness config set KEY VALUE

    Use 'codemie-test-harness config vars' to see all available credentials.
    """
    ctx.ensure_object(dict)

    # Ensure env vars. CLI args override env/config.
    provided = {
        # auth/api
        KEY_AUTH_SERVER_URL: auth_server_url,
        KEY_AUTH_CLIENT_ID: auth_client_id,
        KEY_AUTH_CLIENT_SECRET: auth_client_secret,
        KEY_AUTH_USERNAME: auth_username,
        KEY_AUTH_PASSWORD: auth_password,
        KEY_AUTH_REALM_NAME: auth_realm_name,
        KEY_CODEMIE_API_DOMAIN: api_domain,
    }
    for k, v in provided.items():
        if v is not None and v != "":
            os.environ[k] = str(v)
    # populate any missing values from saved config
    ensure_env_from_config()


# Register subcommands
cli.add_command(config_cmd)
cli.add_command(run_cmd)
cli.add_command(assistant_cmd)
cli.add_command(workflow_cmd)
cli.add_command(marks_cmd)


if __name__ == "__main__":  # pragma: no cover
    cli()
