# Copyright (C) 2025 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Quota command
=============

Manage quota configurations for BuildGrid instances and bot cohorts.
"""

import sys
from typing import Any

import click
from google.protobuf import json_format

from buildgrid.server.client.channel import setup_channel
from buildgrid.server.client.quota import QuotaInterface
from buildgrid.server.exceptions import InvalidArgumentError, NotFoundError

from ..cli import pass_context


@click.group(name="quota", short_help="Manage quota configurations.")
@click.option(
    "--remote",
    type=click.STRING,
    default="http://localhost:50051",
    show_default=True,
    help="Remote execution server's URL (port defaults to 50051 if no specified).",
)
@click.option(
    "--auth-token",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Authorization token for the remote.",
)
@click.option(
    "--client-key",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Private client key for TLS (PEM-encoded).",
)
@click.option(
    "--client-cert",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Public client certificate for TLS (PEM-encoded).",
)
@click.option(
    "--server-cert",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Public server certificate for TLS (PEM-encoded).",
)
@click.option(
    "--instance-name", type=click.STRING, default=None, show_default=True, help="Targeted farm instance name."
)
@click.option("--action-id", type=str, help="Action ID.")
@click.option("--invocation-id", type=str, help="Tool invocation ID.")
@click.option("--correlation-id", type=str, help="Correlated invocation ID.")
@pass_context
def cli(
    context: Any,
    remote: str,
    instance_name: str,
    auth_token: str,
    client_key: str,
    client_cert: str,
    server_cert: str,
    action_id: str,
    invocation_id: str,
    correlation_id: str,
) -> None:
    """Entry point for the bgd-quota CLI command group."""
    try:
        context.channel, _ = setup_channel(
            remote,
            auth_token=auth_token,
            client_key=client_key,
            client_cert=client_cert,
            server_cert=server_cert,
            action_id=action_id,
            tool_invocation_id=invocation_id,
            correlated_invocations_id=correlation_id,
        )

    except InvalidArgumentError as e:
        click.echo(f"Error: {e}.", err=True)
        sys.exit(-1)

    context.instance_name = instance_name


@cli.command("get", short_help="Get quota configuration for an instance and bot cohort.")
@click.argument("instance_name", type=click.STRING, required=True)
@click.argument("bot_cohort", type=click.STRING, required=True)
@click.option("--json", is_flag=True, show_default=True, help="Print quota configuration in JSON format.")
@pass_context
def get_quota(context: Any, instance_name: str, bot_cohort: str, json: bool) -> None:
    """Get the quota configuration for a specific instance and bot cohort."""
    quota_interface = QuotaInterface(context.channel)

    try:
        quota = quota_interface.get_instance_quota(instance_name, bot_cohort)

        if json:
            click.echo(json_format.MessageToJson(quota))
        else:
            click.echo(f"Quota configuration for instance '{instance_name}', bot cohort '{bot_cohort}':")
            click.echo(f"  Instance name: {quota.instance_name}")
            click.echo(f"  Bot cohort: {quota.bot_cohort}")
            click.echo(f"  Min quota: {quota.min_quota}")
            click.echo(f"  Max quota: {quota.max_quota}")
            click.echo(f"  Current usage: {quota.current_usage}")

    except NotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(-1)
    except ConnectionError as e:
        click.echo(f"Error: Connection failed: {e}", err=True)
        sys.exit(-1)


@cli.command("put", short_help="Set or update quota configuration for an instance and bot cohort.")
@click.argument("instance_name", type=click.STRING, required=True)
@click.argument("bot_cohort", type=click.STRING, required=True)
@click.option("--min-quota", type=click.INT, required=True, help="Minimum quota limit for the instance.")
@click.option("--max-quota", type=click.INT, required=True, help="Maximum quota limit for the instance.")
@pass_context
def put_quota(context: Any, instance_name: str, bot_cohort: str, min_quota: int, max_quota: int) -> None:
    """Set or update the quota configuration for a specific instance and bot cohort."""
    # Validate that min_quota <= max_quota
    if min_quota > max_quota:
        click.echo("Error: min-quota cannot be greater than max-quota", err=True)
        sys.exit(-1)

    quota_interface = QuotaInterface(context.channel)

    try:
        quota_interface.put_instance_quota(instance_name, bot_cohort, min_quota, max_quota)
        click.echo("Successfully set quota configuration:")
        click.echo(f"  Instance name: {instance_name}")
        click.echo(f"  Bot cohort: {bot_cohort}")
        click.echo(f"  Min quota: {min_quota}")
        click.echo(f"  Max quota: {max_quota}")

    except ConnectionError as e:
        click.echo(f"Error: Connection failed: {e}", err=True)
        sys.exit(-1)


@cli.command("delete", short_help="Delete quota configuration for an instance and bot cohort.")
@click.argument("instance_name", type=click.STRING, required=True)
@click.argument("bot_cohort", type=click.STRING, required=True)
@pass_context
def delete_quota(context: Any, instance_name: str, bot_cohort: str) -> None:
    """Delete the quota configuration for a specific instance and bot cohort."""
    quota_interface = QuotaInterface(context.channel)

    try:
        quota_interface.delete_instance_quota(instance_name, bot_cohort)

        click.echo(
            f"Successfully deleted quota configuration for instance '{instance_name}', bot cohort '{bot_cohort}'"
        )

    except NotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(-1)
    except ConnectionError as e:
        click.echo(f"Error: Connection failed: {e}", err=True)
        sys.exit(-1)
