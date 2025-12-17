"""Authentication helper utilities for Super CLI."""

from typing import Optional
from functools import wraps
from .token_storage import TokenStorage


def is_authenticated() -> bool:
    """Check if user is currently authenticated.

    Returns:
        True if authenticated, False otherwise

    Example:
        >>> if is_authenticated():
        ...     print("User is logged in")
        ... else:
        ...     print("Please login")
    """
    storage = TokenStorage()
    return storage.has_token() and not storage.is_token_expired()


def get_current_user() -> Optional[dict]:
    """Get current authenticated user information.

    Returns:
        User data dictionary or None if not authenticated

    Example:
        >>> user = get_current_user()
        >>> if user:
        ...     username = user.get('user_metadata', {}).get('user_name')
        ...     print(f"Logged in as @{username}")
    """
    if not is_authenticated():
        return None

    storage = TokenStorage()
    return storage.get_user()


def get_access_token() -> Optional[str]:
    """Get current access token.

    Returns:
        Access token string or None if not authenticated

    Example:
        >>> token = get_access_token()
        >>> if token:
        ...     # Use token for API calls
        ...     headers = {'Authorization': f'Bearer {token}'}
    """
    if not is_authenticated():
        return None

    storage = TokenStorage()
    token_data = storage.load_token()
    return token_data.get("access_token") if token_data else None


def get_authenticated_client():
    """Get authenticated Supabase client.

    Returns:
        Authenticated Supabase client or None if not authenticated

    Example:
        >>> client = get_authenticated_client()
        >>> if client:
        ...     response = client.table('agents').select('*').execute()
    """
    if not is_authenticated():
        return None

    try:
        from .supabase_client import SuperOptiXAuth

        storage = TokenStorage()
        token_data = storage.load_token()

        if not token_data:
            return None

        auth = SuperOptiXAuth()

        # Set the session with stored tokens
        auth.client.auth.set_session(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
        )

        return auth

    except Exception:
        return None


def require_auth(func):
    """Decorator to require authentication for CLI commands.

    Displays a helpful message if user is not authenticated.

    Example:
        >>> @click.command()
        ... @require_auth
        ... def pull_agent(name: str):
        ...     '''Pull agent from marketplace (requires auth).'''
        ...     # This code only runs if user is authenticated
        ...     pass
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        from rich.console import Console
        from rich.panel import Panel

        if not is_authenticated():
            console = Console()
            console.print()

            auth_required_panel = Panel(
                "[yellow]⚠️  Authentication Required[/yellow]\n\n"
                "This command requires you to be logged in.\n\n"
                "To authenticate, run:\n"
                "  [cyan]super login[/cyan]\n\n"
                "[dim]Available login methods:[/dim]\n"
                "  • [cyan]super login[/cyan]          - Browser OAuth (recommended)\n"
                "  • [cyan]super login --device[/cyan]  - Device flow\n"
                "  • [cyan]super login --token[/cyan]   - Token-based login",
                border_style="yellow",
                padding=(1, 2),
                title="[bold yellow]🔐 Login Required[/bold yellow]",
            )

            console.print(auth_required_panel)
            console.print()
            return None

        return func(*args, **kwargs)

    return wrapper


def show_auth_status(console=None):
    """Display current authentication status.

    Args:
        console: Rich Console instance (creates new one if not provided)

    Example:
        >>> from rich.console import Console
        >>> console = Console()
        >>> show_auth_status(console)
    """
    from rich.console import Console
    from rich.text import Text

    if console is None:
        console = Console()

    storage = TokenStorage()

    if not storage.has_token():
        status = Text.assemble(
            ("🔓 ", "dim"),
            ("Not logged in", "dim"),
            (" • ", "dim"),
            ("Run ", "dim"),
            ("super login", "cyan"),
            (" to authenticate", "dim"),
        )
        console.print(status)
        return

    user = storage.get_user()
    if not user:
        status = Text.assemble(
            ("⚠️  ", "yellow"),
            ("Invalid session", "yellow"),
            (" • ", "dim"),
            ("Run ", "dim"),
            ("super login", "cyan"),
            (" to re-authenticate", "dim"),
        )
        console.print(status)
        return

    username = user.get("user_metadata", {}).get("user_name", user.get("email", "User"))

    if storage.is_token_expired():
        status = Text.assemble(
            ("⚠️  ", "yellow"),
            ("Session expired", "yellow"),
            (" (was logged in as ", "dim"),
            (f"@{username}", "cyan"),
            (") • ", "dim"),
            ("Run ", "dim"),
            ("super login", "cyan"),
            (" to re-authenticate", "dim"),
        )
        console.print(status)
        return

    status = Text.assemble(
        ("🔐 ", "green"), ("Logged in as ", "dim"), (f"@{username}", "cyan")
    )
    console.print(status)


def refresh_token_if_needed() -> bool:
    """Automatically refresh token if expired or about to expire.

    Returns:
        True if token is valid (or was successfully refreshed), False otherwise

    Example:
        >>> if refresh_token_if_needed():
        ...     # Proceed with authenticated operation
        ...     pass
        ... else:
        ...     print("Please login again")
    """
    storage = TokenStorage()
    token_data = storage.load_token()

    if not token_data:
        return False

    # Check if token is expired or about to expire
    expires_at = token_data.get("expires_at", 0)

    from time import time

    # Refresh if expired or expiring in next 5 minutes
    if time() > (expires_at - 300):
        refresh_token = token_data.get("refresh_token")

        if not refresh_token:
            # No refresh token available
            return False

        try:
            from .supabase_client import SuperOptiXAuth

            auth = SuperOptiXAuth()

            # Refresh the session
            new_session = auth.client.auth.refresh_session(refresh_token)

            # Save new token
            storage.save_token(
                {
                    "access_token": new_session.session.access_token,
                    "refresh_token": new_session.session.refresh_token,
                    "expires_at": new_session.session.expires_at,
                    "user": new_session.user.model_dump()
                    if hasattr(new_session.user, "model_dump")
                    else new_session.user.__dict__,
                }
            )

            return True

        except Exception:
            # Refresh failed, require re-login
            storage.delete_token()
            return False

    return True
