"""Supabase authentication client for Super CLI."""

from typing import Optional

try:
    from supabase import create_client, Client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    create_client = None
    Client = None


class SuperOptiXAuth:
    """Supabase authentication client for Super CLI."""

    # SuperOptiX Backend Credentials (public - safe to embed)
    # The anon key is designed to be public (used in frontend apps)
    # Security is handled by Row Level Security (RLS) in Supabase
    SUPABASE_URL = "https://fffpinwooyqblbpdxicq.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZmZnBpbndvb3lxYmxicGR4aWNxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE0MjUwNDksImV4cCI6MjA3NzAwMTA0OX0.nxLcE3_0jSFhcODLGUfQFErqL8ZO8eDhyCX1Vfx2wuQ"

    def __init__(self):
        """Initialize Supabase client with credentials."""
        if not SUPABASE_AVAILABLE:
            raise ImportError(
                "Supabase is not installed. "
                "This should not happen - supabase is a core dependency. "
                "Try reinstalling: pip install --upgrade superoptix"
            )

        self.supabase_url = self.SUPABASE_URL
        self.supabase_key = self.SUPABASE_ANON_KEY

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def sign_in_with_github_oauth(self, redirect_url: str):
        """Initiate GitHub OAuth flow."""
        return self.client.auth.sign_in_with_oauth(
            {"provider": "github", "options": {"redirect_to": redirect_url}}
        )

    def exchange_code_for_session(self, code: str):
        """Exchange OAuth code for session.

        Args:
            code: The OAuth authorization code from the callback

        Returns:
            AuthResponse with session and user data
        """
        # Latest Supabase SDK (v2.x) expects a dict, not a string
        # The code_verifier is automatically retrieved from storage
        # (it was stored during sign_in_with_oauth)
        return self.client.auth.exchange_code_for_session({"auth_code": code})

    def sign_in_with_oauth_token(self, provider: str, token: str):
        """Sign in with OAuth provider token."""
        return self.client.auth.sign_in_with_id_token(
            {"provider": provider, "token": token}
        )

    def get_session(self):
        """Get current session."""
        return self.client.auth.get_session()

    def get_user(self):
        """Get current user."""
        return self.client.auth.get_user()

    def sign_out(self):
        """Sign out current user."""
        return self.client.auth.sign_out()

    def set_session(self, access_token: str, refresh_token: Optional[str] = None):
        """Set session with tokens."""
        self.client.auth.set_session(access_token, refresh_token)
        return self.get_user()

    def refresh_session(self, refresh_token: str):
        """Refresh session with refresh token."""
        return self.client.auth.refresh_session(refresh_token)

    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists by attempting to query it.

        Args:
            table_name: Name of the table to check

        Returns:
            True if table exists, False otherwise
        """
        try:
            # Try to select 0 rows to check if table exists
            self.client.table(table_name).select("id").limit(0).execute()
            return True
        except Exception:
            return False

    def track_login(self, user_id: str) -> dict:
        """Track user login to database.

        Args:
            user_id: User ID from auth

        Returns:
            dict with 'success' (bool) and optional 'message' (str)
        """
        try:
            from datetime import datetime

            # First, check if table exists
            table_exists = self.check_table_exists("user_events")
            if not table_exists:
                return {
                    "success": False,
                    "message": "user_events table does not exist",
                    "setup_required": True,
                }

            # Attempt to insert login event
            response = (
                self.client.table("user_events")
                .insert(
                    {
                        "event_type": "login",
                        "user_id": user_id,
                        "created_at": datetime.utcnow().isoformat(),
                    }
                )
                .execute()
            )

            # Check if insert was successful
            if hasattr(response, "data") and response.data:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "message": "Insert returned no data (might be an RLS policy issue)",
                    "setup_required": False,
                }

        except Exception as e:
            error_message = str(e)
            is_table_missing = (
                "does not exist" in error_message.lower()
                or "relation" in error_message.lower()
            )
            is_permission_issue = (
                "permission" in error_message.lower()
                or "policy" in error_message.lower()
            )

            return {
                "success": False,
                "message": error_message,
                "setup_required": is_table_missing,
                "permission_issue": is_permission_issue,
            }
