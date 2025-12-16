from typing import Annotated

from typer import Option

from spiral.api.organizations import CreateOrgRequest
from spiral.api.types import OrgId
from spiral.cli import CONSOLE, AsyncTyper, state
from spiral.core.authn import DeviceCodeAuth

app = AsyncTyper()


@app.command()
def sync(
    org_id: OrgId | None = None,
):
    state.spiral.api._admin.sync_orgs()

    for membership in state.spiral.api._admin.sync_memberships(org_id):
        CONSOLE.print(membership)


# NOTE(marko): This might only be used in testing scenarios.
@app.command(help="Create a new organization.")
def create_org(
    name: Annotated[str | None, Option(help="The human-readable name of the organization.")] = None,
):
    res = state.spiral.api.organizations.create(CreateOrgRequest(name=name))

    # Authenticate to the new organization
    DeviceCodeAuth.default().authenticate(org_id=res.org.id)

    CONSOLE.print(f"{res.org.name} [dim]{res.org.id}[/dim]")
