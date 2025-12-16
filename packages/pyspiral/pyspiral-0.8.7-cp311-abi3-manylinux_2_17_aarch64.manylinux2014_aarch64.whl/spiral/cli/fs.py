import os
from typing import Literal

import questionary
import typer
from typer import Option

from spiral.api.filesystems import (
    BuiltinFileSystem,
    GCSFileSystem,
    S3FileSystem,
    S3LikeFileSystem,
    UpstreamFileSystem,
)
from spiral.cli import CONSOLE, AsyncTyper, state
from spiral.cli.types import ProjectArg, ask_project

app = AsyncTyper(short_help="File Systems.")


@app.command(help="Show the file system configured for project.")
def show(project: ProjectArg):
    file_system = state.spiral.api.file_systems.get_file_system(project)
    CONSOLE.print(file_system)


def ask_provider():
    res = state.spiral.api.file_systems.list_providers()
    return questionary.select("Select a file system provider", choices=res).ask()


@app.command(help="Update a project's default file system.")
def update(
    project: ProjectArg,
    type_: Literal["builtin", "s3", "s3like", "gcs", "upstream"] = Option(
        None, "--type", help="Type of the file system."
    ),
    provider: str = Option(None, help="Provider, when using `builtin` type."),
    endpoint: str = Option(None, help="Endpoint, when using `s3` or `s3like` type."),
    region: str = Option(
        None,
        help="Region, when using `s3`, `s3like` or `gcs` type (defaults to `auto` for `s3` when `endpoint` is set).",
    ),
    bucket: str = Option(None, help="Bucket, when using `s3` or `gcs` type."),
    role_arn: str = Option(None, help="Role ARN to assume, when using `s3` type."),
    skip_confirm: bool = Option(False, "--yes", "-y", help="Skip confirmation prompt."),
):
    if type_ == "builtin":
        provider = provider or ask_provider()
        file_system = BuiltinFileSystem(provider=provider)

    elif type_ == "upstream":
        upstream_project = ask_project(title="Select a project to use as file system.")
        file_system = UpstreamFileSystem(project_id=upstream_project)

    elif type_ == "s3":
        if role_arn is None:
            raise ValueError("--role-arn is required for S3 provider.")
        if not role_arn.startswith("arn:aws:iam::") or ":role/" not in role_arn:
            raise ValueError("Invalid role ARN format. Expected `arn:aws:iam::<account>:role/<role_name>`")
        if bucket is None:
            raise ValueError("--bucket is required for S3 provider.")
        region = region or ("auto" if endpoint else None)
        file_system = S3FileSystem(bucket=bucket, role_arn=role_arn, region=region)
        if endpoint:
            file_system.endpoint = endpoint

    elif type_ == "s3like":
        if endpoint is None or region is None or bucket is None:
            raise ValueError("--endpoint, --region, --bucket are required for `s3like`.")

        access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", None)
        secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
        if access_key_id is None or secret_access_key is None:
            raise ValueError("Environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` must be set.")

        if not skip_confirm:
            confirm = questionary.confirm(
                "Confirm using `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as file system keys?",
                default=False,
            ).ask()
            if not confirm:
                CONSOLE.print("Aborted.")
                raise typer.Exit(0)

        file_system = S3LikeFileSystem(
            endpoint=endpoint,
            region=region,
            bucket=bucket,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )

    elif type_ == "gcs":
        if region is None or bucket is None:
            raise ValueError("--region and --bucket is required for GCS provider.")
        file_system = GCSFileSystem(bucket=bucket, region=region)

    else:
        raise ValueError(f"Unknown file system type: {type_}")

    fs = state.spiral.api.file_systems.update_file_system(project, file_system)
    CONSOLE.print(fs)


@app.command(help="Lists the available built-in file system providers.")
def list_providers():
    for provider in state.spiral.api.file_systems.list_providers():
        CONSOLE.print(provider)
