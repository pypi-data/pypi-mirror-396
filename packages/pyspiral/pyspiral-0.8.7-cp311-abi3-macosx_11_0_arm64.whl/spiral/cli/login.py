import jwt

from spiral.cli import CONSOLE, state
from spiral.core.authn import DeviceCodeAuth


def command(org_id: str | None = None, force: bool = False, show_token: bool = False):
    token = DeviceCodeAuth.default().authenticate(force=force, org_id=org_id)
    CONSOLE.print("Successfully logged in.")
    if show_token:
        CONSOLE.print(token.expose_secret(), soft_wrap=True)


def whoami():
    """Display the current user's information."""
    payload = jwt.decode(state.spiral.authn.token().expose_secret(), options={"verify_signature": False})

    if "org_id" in payload:
        CONSOLE.print(f"{payload['org_id']}")
    CONSOLE.print(f"{payload['sub']}")


def logout():
    DeviceCodeAuth.default().logout()
    CONSOLE.print("Logged out.")
