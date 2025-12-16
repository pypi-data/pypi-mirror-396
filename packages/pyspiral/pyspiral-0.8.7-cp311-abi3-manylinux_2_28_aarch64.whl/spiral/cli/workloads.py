from typing import Annotated

import pyperclip
import questionary
from questionary import Choice
from typer import Argument, Option

from spiral.api.workloads import (
    CreateWorkloadRequest,
    CreateWorkloadResponse,
    IssueWorkloadCredentialsResponse,
    Workload,
)
from spiral.cli import CONSOLE, ERR_CONSOLE, AsyncTyper, printer, state
from spiral.cli.types import ProjectArg

app = AsyncTyper()


@app.command(help="List workloads.")
def ls(
    project: ProjectArg,
):
    workloads = list(state.spiral.api.workloads.list(project))
    CONSOLE.print(printer.table_of_models(Workload, workloads, fields=["id", "project_id", "name"]))


@app.command(help="Create a new workload.")
def create(
    project: ProjectArg,
    name: Annotated[str | None, Option(help="Friendly name for the workload.")] = None,
):
    res: CreateWorkloadResponse = state.spiral.api.workloads.create(project, CreateWorkloadRequest(name=name))
    CONSOLE.print(f"{res.workload.id}")


@app.command(help="Deactivate a workload. Removes all associated credentials.")
def deactivate(
    workload_id: Annotated[str, Argument(help="Workload ID.")],
):
    state.spiral.api.workloads.deactivate(workload_id)
    CONSOLE.print(f"Deactivated workload {workload_id}")


@app.command(help="Issue new workflow credentials.")
def issue_creds(
    workload_id: Annotated[str, Argument(help="Workload ID.")],
    skip_prompt: Annotated[bool, Option(help="Skip prompt and print secret to console.")] = False,
):
    res: IssueWorkloadCredentialsResponse = state.spiral.api.workloads.issue_credentials(workload_id)

    if skip_prompt:
        CONSOLE.print(f"[green]SPIRAL_CLIENT_ID[/green] {res.client_id}")
        CONSOLE.print(f"[green]SPIRAL_CLIENT_SECRET[/green] {res.client_secret}")
    else:
        while True:
            choice = questionary.select(
                "What would you like to do with the secret? You will not be able to see this secret again!",
                choices=[
                    Choice(title="Copy to clipboard", value=1),
                    Choice(title="Print to console", value=2),
                    Choice(title="Exit", value=3),
                ],
            ).ask()

            if choice == 1:
                pyperclip.copy(res.client_secret)
                CONSOLE.print("[green]Secret copied to clipboard![/green]")
                break
            elif choice == 2:
                CONSOLE.print(f"[green]SPIRAL_CLIENT_SECRET[/green] {res.client_secret}")
                break
            elif choice == 3:
                break
            else:
                ERR_CONSOLE.print("Invalid choice. Please try again.")

        CONSOLE.print(f"[green]SPIRAL_CLIENT_ID[/green] {res.client_id}")


@app.command(help="Revoke workflow credentials.")
def revoke_creds(
    client_id: Annotated[str, Argument(help="Client ID to revoke.")],
):
    state.spiral.api.workloads.revoke_credentials(client_id)
    CONSOLE.print(f"Revoked credentials for client ID {client_id}")
