"""Authentication commands for Super CLI."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from superoptix.cli.auth.token_storage import TokenStorage
from superoptix.cli.auth.supabase_client import SuperOptiXAuth
from superoptix.cli.auth.oauth_flow import BrowserOAuthFlow
from superoptix.cli.commands.thinking_animation import ThinkingAnimation

console = Console()


def login(args):
    """Login to SuperOptiX with GitHub."""

    # Extract token from argparse Namespace
    token = getattr(args, "token", None)

    storage = TokenStorage()

    # Check if already logged in
    if storage.has_token():
        console.print()
        console.print(
            Panel(
                "[yellow]You are already logged in.[/yellow]\n\n"
                "Run [cyan]super logout[/cyan] first to switch accounts.",
                border_style="yellow",
                title="[bold]⚠️  Already Authenticated[/bold]",
                padding=(1, 2),
            )
        )
        console.print()
        return

    console.print()

    # Show login header
    header = Panel(
        Text.assemble(
            ("🔐 ", "cyan"),
            ("Login to SuperOptiX", "bold cyan"),
            ("\n\n", ""),
            ("Authenticate with GitHub to:", "dim"),
            ("\n  • ", "dim"),
            ("Save and sync your agents", "white"),
            ("\n  • ", "dim"),
            ("Access the marketplace", "white"),
            ("\n  • ", "dim"),
            ("Collaborate with teams", "white"),
        ),
        border_style="bright_cyan",
        padding=(1, 2),
    )
    console.print(header)
    console.print()

    # Handle token-based login
    if token:
        _login_with_token(token, storage)
        return

    # Default: Browser OAuth flow
    _login_with_browser(storage)


def _login_with_browser(storage: TokenStorage):
    """Login using browser OAuth flow."""

    animator = ThinkingAnimation(console)

    try:
        # Initialize Supabase auth
        auth = SuperOptiXAuth()

        # Start OAuth flow (pass Supabase client for PKCE support)
        oauth_flow = BrowserOAuthFlow(auth.client)

        # Start the callback server FIRST (before displaying URL)
        if not oauth_flow.start_server():
            console.print()
            console.print("[red]❌ Failed to start callback server[/red]")
            console.print(
                "[dim]Port 54321 might be in use. Try closing other applications.[/dim]"
            )
            console.print()
            return

        # Get OAuth URL (server is already running now!)
        oauth_url = oauth_flow.get_oauth_url()

        console.print()
        console.print("[bold cyan]🔗 GitHub OAuth Login[/bold cyan]")
        console.print()
        console.print("[green]✅ Callback server ready on port 54321[/green]")
        console.print()
        console.print(
            "[bold yellow]Click the URL below to open in your browser:[/bold yellow]"
        )
        console.print()

        # Print URL as clickable link
        # Most terminals support clickable URLs
        from rich.console import Console as RichConsole
        from rich.markdown import Markdown

        # Create clickable link
        link_text = f"[🔗 Click here to authenticate]({oauth_url})"
        console.print(Markdown(link_text))

        console.print()
        console.print("[dim]Or copy and paste this URL:[/dim]")

        # Print plain URL for copying
        url_console = RichConsole(width=500, legacy_windows=False)
        url_console.print(f"[cyan]{oauth_url}[/cyan]")

        console.print()
        console.print("[dim]💡 After authenticating, return here and wait...[/dim]")
        console.print()

        # Show waiting animation
        animator.thinking("⏳ Waiting for authentication", duration=0.5)

        # Wait for callback
        auth_code = oauth_flow.wait_for_callback(timeout=300)
        animator.stop()

        if auth_code:
            # Exchange code for session
            console.print()
            animator.thinking("🔑 Completing authentication", duration=1.0)

            try:
                session_response = auth.exchange_code_for_session(auth_code)
                animator.stop()

                # Handle different response formats from Supabase SDK
                session = None
                user = None

                # Try object attributes first (Supabase v2.x)
                if hasattr(session_response, "session"):
                    session = session_response.session
                    user = session_response.user
                # Try dict format (Supabase v1.x)
                elif isinstance(session_response, dict):
                    session = session_response.get("session")
                    user = session_response.get("user")
                # Try nested data attribute
                elif hasattr(session_response, "data"):
                    session = (
                        session_response.data.get("session")
                        if isinstance(session_response.data, dict)
                        else session_response.data.session
                    )
                    user = (
                        session_response.data.get("user")
                        if isinstance(session_response.data, dict)
                        else session_response.data.user
                    )
                else:
                    raise ValueError(
                        f"Unexpected response format: {type(session_response)}"
                    )

                # Extract token data
                if hasattr(session, "access_token"):
                    access_token = session.access_token
                    refresh_token = session.refresh_token
                    expires_at = session.expires_at
                elif isinstance(session, dict):
                    access_token = session["access_token"]
                    refresh_token = session.get("refresh_token")
                    expires_at = session.get("expires_at")
                else:
                    raise ValueError(f"Unexpected session type: {type(session)}")

                # Extract user data
                if hasattr(user, "model_dump"):
                    user_data = user.model_dump()
                elif hasattr(user, "__dict__"):
                    user_data = user.__dict__
                elif isinstance(user, dict):
                    user_data = user
                else:
                    user_data = {"id": str(user)}

                # Convert datetime objects to strings for JSON serialization
                def make_json_serializable(obj):
                    """Recursively convert datetime objects to ISO format strings."""
                    from datetime import datetime

                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    elif isinstance(obj, dict):
                        return {k: make_json_serializable(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [make_json_serializable(item) for item in obj]
                    else:
                        return obj

                user_data = make_json_serializable(user_data)
                expires_at = (
                    expires_at.isoformat()
                    if hasattr(expires_at, "isoformat")
                    else expires_at
                )

                # Save token
                storage.save_token(
                    {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expires_at": expires_at,
                        "user": user_data,
                    }
                )

                # Track login
                user_id = user_data.get("id") or user_data.get("user_id")
                if user_id:
                    result = auth.track_login(user_id)
                    if not result.get("success"):
                        if result.get("setup_required"):
                            _show_database_setup_warning()
                        elif result.get("message"):
                            # Show error details for debugging
                            console.print()
                            console.print(
                                f"[yellow]⚠️  Login tracking failed: {result.get('message')}[/yellow]"
                            )
                            console.print()

                # Show success
                _show_login_success(user)

            except Exception as e:
                animator.stop()
                console.print()
                console.print(f"[red]❌ Failed to complete authentication:[/red] {e}")
                console.print(
                    f"[dim]Response type: {type(session_response) if 'session_response' in locals() else 'unknown'}[/dim]"
                )
                console.print()

        else:
            console.print()
            console.print("[red]❌ Authentication failed or timed out[/red]")
            console.print()
            console.print("[yellow]Common issues:[/yellow]")
            console.print("  1. [dim]Browser blocked localhost connection[/dim]")
            console.print("  2. [dim]Supabase redirect URL not configured[/dim]")
            console.print()
            console.print("[bold]To fix:[/bold]")
            console.print(
                "  • Add [cyan]http://localhost:54321/callback[/cyan] to Supabase redirect URLs"
            )
            console.print(
                "  • Go to: [link]https://supabase.com/dashboard[/link] → Auth → URL Configuration"
            )
            console.print("  • Set Site URL to [cyan]http://localhost:54321[/cyan]")
            console.print()
            console.print(
                "[dim]Or use: [cyan]super login --token YOUR_TOKEN[/cyan][/dim]"
            )
            console.print()

    except Exception as e:
        console.print()
        console.print(f"[red]❌ Error:[/red] {e}")
        console.print(
            "[dim]Try using token-based login: [cyan]super login --token YOUR_TOKEN[/cyan][/dim]"
        )
        console.print()


def _login_with_token(token: str, storage: TokenStorage):
    """Login using access token directly."""

    animator = ThinkingAnimation(console)

    try:
        animator.thinking("🔑 Verifying token", duration=1.0)

        auth = SuperOptiXAuth()
        user = auth.set_session(token)

        animator.stop()

        # Get user data
        user_data = user.model_dump() if hasattr(user, "model_dump") else user.__dict__

        # Save token
        storage.save_token({"access_token": token, "user": user_data})

        # Track login
        user_id = user_data.get("id") or user_data.get("user_id")
        if user_id:
            result = auth.track_login(user_id)
            if not result.get("success"):
                if result.get("setup_required"):
                    _show_database_setup_warning()
                elif result.get("message"):
                    # Show error details for debugging
                    console.print()
                    console.print(
                        f"[yellow]⚠️  Login tracking failed: {result.get('message')}[/yellow]"
                    )
                    console.print()

        # Show success
        _show_login_success(user)

    except Exception as e:
        animator.stop()
        console.print()
        console.print(f"[red]❌ Invalid token:[/red] {e}")
        console.print()


def _show_database_setup_warning():
    """Show warning about database setup being required."""
    console.print()
    console.print(
        Panel(
            Text.assemble(
                ("⚠️  ", "yellow"),
                ("Database Setup Required", "bold yellow"),
                ("\n\n", ""),
                ("The user_events table needs to be set up in Supabase.\n", "white"),
                ("This is a one-time setup for the Supabase admin.\n\n", "dim"),
                ("Setup Instructions:\n", "bold"),
                ("1. Go to your Supabase project SQL Editor\n", "dim"),
                ("2. Run the SQL from: ", "dim"),
                ("supabase_user_events_setup.sql\n\n", "cyan"),
                ("Location: ", "dim"),
                (
                    "https://github.com/SuperagenticAI/superoptix/blob/main/supabase_user_events_setup.sql",
                    "blue underline",
                ),
            ),
            border_style="yellow",
            padding=(1, 2),
        )
    )
    console.print()


def _show_login_success(user):
    """Show successful login message."""

    user_metadata = (
        user.user_metadata
        if hasattr(user, "user_metadata")
        else user.get("user_metadata", {})
    )
    email = user.email if hasattr(user, "email") else user.get("email", "Unknown")

    username = (
        user_metadata.get("user_name")
        or user_metadata.get("preferred_username")
        or email
    )

    console.print()

    success_panel = Panel(
        Text.assemble(
            ("✅ ", "green"),
            ("Successfully authenticated!", "bold green"),
            ("\n\n", ""),
            ("Logged in as: ", "dim"),
            (f"@{username}", "bold cyan"),
            ("\n", ""),
            ("Email: ", "dim"),
            (f"{email}", "cyan"),
        ),
        border_style="bright_green",
        padding=(1, 2),
        title="[bold green]🎉 Welcome to SuperOptiX![/bold green]",
    )

    console.print(success_panel)
    console.print()


def logout(args):
    """Logout from SuperOptiX."""

    storage = TokenStorage()

    if not storage.has_token():
        console.print()
        console.print("[yellow]You are not logged in.[/yellow]")
        console.print()
        return

    # Get user info before logout
    token_data = storage.load_token()
    user = token_data.get("user", {})
    user_metadata = user.get("user_metadata", {})
    username = (
        user_metadata.get("user_name")
        or user_metadata.get("preferred_username")
        or user.get("email", "User")
    )

    # Delete token
    storage.delete_token()

    # Sign out from Supabase
    try:
        auth = SuperOptiXAuth()
        auth.sign_out()
    except:
        pass

    console.print()
    console.print(
        Panel(
            f"[green]✅ Logged out successfully![/green]\n\n"
            f"[dim]Goodbye, @{username}![/dim]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )
    console.print()


def whoami(args):
    """Show current logged in user."""

    storage = TokenStorage()

    if not storage.has_token():
        console.print()
        console.print("[yellow]Not logged in.[/yellow]")
        console.print("[dim]Run [cyan]super login[/cyan] to authenticate.[/dim]")
        console.print()
        return

    token_data = storage.load_token()
    user = token_data.get("user", {})
    user_metadata = user.get("user_metadata", {})

    username = (
        user_metadata.get("user_name")
        or user_metadata.get("preferred_username")
        or user.get("email", "Unknown")
    )
    email = user.get("email", "N/A")

    console.print()
    console.print(
        Panel(
            Text.assemble(
                ("👤 ", "cyan"),
                ("Logged in as", "bold cyan"),
                ("\n\n", ""),
                ("Username: ", "dim"),
                (f"@{username}\n", "bold cyan"),
                ("Email: ", "dim"),
                (f"{email}\n", "cyan"),
            ),
            border_style="bright_cyan",
            padding=(1, 2),
            title="[bold cyan]User Info[/bold cyan]",
        )
    )
    console.print()
