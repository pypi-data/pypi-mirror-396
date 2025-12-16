import webbrowser

import jwt
import typer
from rich.table import Table

from spiral.api.organizations import InviteUserRequest, OrgRole, PortalLinkIntent, PortalLinkRequest
from spiral.cli import CONSOLE, ERR_CONSOLE, AsyncTyper, state
from spiral.cli.types import OrganizationArg
from spiral.core.authn import DeviceCodeAuth

app = AsyncTyper(short_help="Org admin.")


@app.command(help="Switch the active organization.")
def switch(org_id: OrganizationArg):
    DeviceCodeAuth.default().authenticate(org_id=org_id)
    CONSOLE.print(f"Switched to organization: {org_id}")


@app.command(help="List organizations.")
def ls():
    org_id = current_org_id()

    table = Table("", "id", "name", "role", title="Organizations")
    for m in state.spiral.api.organizations.list_memberships():
        table.add_row("👉" if m.org.id == org_id else "", m.org.id, m.org.name, m.role)

    CONSOLE.print(table)


@app.command(help="Invite a user to the organization.")
def invite(email: str, role: OrgRole = OrgRole.MEMBER, expires_in_days: int = 7):
    state.spiral.api.organizations.invite_user(
        InviteUserRequest(email=email, role=role, expires_in_days=expires_in_days)
    )
    CONSOLE.print(f"Invited {email} as a {role.value}.")


@app.command(help="Configure single sign-on for your organization.")
def sso():
    _do_action(PortalLinkIntent.SSO)


@app.command(help="Configure directory services for your organization.")
def directory():
    _do_action(PortalLinkIntent.DIRECTORY_SYNC)


@app.command(help="Configure audit logs for your organization.")
def audit_logs():
    _do_action(PortalLinkIntent.AUDIT_LOGS)


@app.command(help="Configure log streams for your organization.")
def log_streams():
    _do_action(PortalLinkIntent.LOG_STREAMS)


@app.command(help="Configure domains for your organization.")
def domains():
    _do_action(PortalLinkIntent.DOMAIN_VERIFICATION)


@app.command(help="Configure bring-your-own-key for your organization.")
def keys():
    _do_action(PortalLinkIntent.BYOK)


def _do_action(intent: PortalLinkIntent):
    res = state.spiral.api.organizations.portal_link(PortalLinkRequest(intent=intent))
    CONSOLE.print(f"Opening the configuration portal:\n{res.url}")
    webbrowser.open(res.url)


def current_org_id():
    if token := state.spiral.authn.token():
        if org_id := jwt.decode(token.expose_secret(), options={"verify_signature": False}).get("org_id"):
            return org_id
    ERR_CONSOLE.print("You are not logged in to an organization.")
    raise typer.Exit(1)
